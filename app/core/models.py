from app import mongo

class Core:
    @staticmethod
    def get_categories():
        """
        Retrieves the list of categories from the database.

        This method queries the database to retrieve all category documents
        from the categories collection and returns them as a list.

        Returns:
            list: A list of category documents from the categories collection.
            If an exception occurs, returns an empty list.

        Raises:
            Exception: If there is an issue with the database query, the
            exception is caught and an error message is printed.
        """
        try:
            categories = list(mongo.db.categories.find())
            return categories
        except Exception as e:
            print(f"Error in get_categories method: {e}")
            return []

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
    def get_roles():
        """
        Retrieves a list of all roles from the database.

        This static method queries the database for all documents in the
        'roles' collection and returns them as a list.

        Returns:
            list: A list of all roles from the database.
        """
        return list(mongo.db.roles.find())
