from bson.objectid import ObjectId
from app import mongo
from app.questions.models import Question


class Group:
    # Docstrings written by GPT4o and edited by myself.
    @staticmethod
    def get_groups_by_role(role, username):
        """
        Retrieves a list of groups from the database filtered by the user's role and username.

        This method queries the database to retrieve groups based on the provided user role and username.
        - If the role is 'Admin', it retrieves all groups.
        - If the role is 'Tutor', it retrieves groups where the tutor is the specified username.
        - If the role is 'Student', it retrieves groups where the student list includes the specified username.
        - For any other roles, it returns an empty list.

        Args:
            role (str): The role of the user (e.g., 'Admin', 'Tutor', 'Student').
            username (str): The username of the user to filter the groups by.

        Returns:
            list: A list of groups filtered by the user's role and username. If an exception occurs, it returns an empty list.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            if role == 'Admin':
                groups = list(mongo.db.groups.find())
            elif role == 'Tutor':
                groups = list(mongo.db.groups.find({"tutor": username}))
            elif role == 'Student':
                groups = list(mongo.db.groups.find({"students": username}))
            else:
                groups = []

            return groups
        
        except Exception as e:
            print(f'Error in get_groups_by_role method: {e}')


    @staticmethod
    def get_group_by_id(group_id):
        """
        Retrieves a group from the database by its ID.

        This method queries the database to find a group document that matches the provided group ID.

        Args:
            group_id (str): The ID of the group to be retrieved.

        Returns:
            dict: The group document matching the provided ID, or None if an exception occurs.

        Raises:
            Exception: If there is an issue with the database query, the exception is caught and an error message is printed.
        """
        try:
            group = mongo.db.groups.find_one({"_id": group_id})

            return group
        
        except Exception as e:
            print(f'Error in get_group_by_id method: {e}')
            return None


    @staticmethod
    def add_student_to_group(group_id, username):
        """
        Adds a student to a group's students list in the database.

        This method updates the specified group by adding the provided username to the group's students list.

        Args:
            group_id (str): The ID of the group to which the student will be added.
            username (str): The username of the student to be added to the group.

        Raises:
            Exception: If there is an issue with updating the group in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.groups.update_one(
                {'_id': ObjectId(group_id)},
                {'$push': {'students': username}}
            )

        except Exception as e:
            print(f'Error in add_student_to_group method: {e}')


    @staticmethod
    def remove_student(group_id, username):
        """
        Removes a student from a group's students list in the database.

        This method updates the specified group by removing the provided username from the group's students list.

        Args:
            group_id (str): The ID of the group from which the student will be removed.
            username (str): The username of the student to be removed from the group.

        Raises:
            Exception: If there is an issue with updating the group in the database, the exception is caught and an error message is printed.
        """
        try:
            mongo.db.groups.update_one(
                {'_id': ObjectId(group_id)},
                {'$pull': {'students': username}}
            )

        except Exception as e:
            print(f'Error in remove_student method: {e}')


    @staticmethod
    def insert_group(tutor, provider, level, year, weekday):
        """
        Inserts a new group into the database.

        This method creates a group document with the provided tutor, provider, level, year,
        and weekday, and inserts it into the groups collection in the database. The students list
        is initialized as an empty list.

        Args:
            tutor (str): The username of the tutor for the group.
            provider (str): The provider associated with the group.
            level (str): The level of the group.
            year (int): The year the group is associated with.
            weekday (str): The day of the week the group meets.

        Raises:
            Exception: If there is an issue with inserting the group into the database, the exception is caught and an error message is printed.
        """
        try:
            group = {
                "tutor": tutor,
                "provider": provider,
                "level": level,
                "year": year,
                "weekday": weekday,
                "students": []
            }
            mongo.db.groups.insert_one(group)
            
        except Exception as e:
            print(f"Error in insert_group method: {e}")

    
    @staticmethod
    def get_levels():
        """
        Retrieves a list of levels from the database.

        Returns:
            list: A list of level documents from the levels collection.
        """
        return list(mongo.db.levels.find())
    

    @staticmethod
    def get_providers():
        """
        Retrieves a list of providers from the database.

        Returns:
            list: A list of provider documents from the providers collection.
        """
        return list(mongo.db.providers.find())
    

    @staticmethod
    def delete_group(group_id):
        """
        Deletes a group from the database.

        This method finds a group by its group_id, deletes any associated questions, 
        and then deletes the group itself from the database.

        Args:
            group_id (str): The unique identifier of the group to be deleted.

        Raises:
            Exception: If there is an issue with deleting the group in the database, the exception is caught and an error message is printed.
        """
        try:
            question = mongo.db.questions.find_one({"group_id": ObjectId(group_id)})
            if question:
                Question.delete_question(question._id)
            mongo.db.groups.delete_one({"_id": ObjectId(group_id)})
        except Exception as e:
            print(f"Error in delete_group method: {e}")

