# Cydymiaith Testing Documentation

Go to [README.md](README.md)

## Table of contents

> 1. User Stories Testing
> 2. Feature Testing
> 3. Defensive Programming Testing
> 4. Responsiveness Testing
> 5. Browser Testing
> 6. Automated Testing
>> 1. HTML Validator
>> 2. CSS Validator
>> 3. PEP8 CI Python Linter (https://pep8ci.herokuapp.com/)
>> 4. WAVE
>> 5. Lighthouse
> 7. Bugs

## User Stories Testing

[Back to top](#cydymiaith-testing-documentation)



## Feature Testing

[Back to top](#cydymiaith-testing-documentation)

Please note that these tests flow sequentially.

### Unregistered Users

#### Navigation

1) Navigate to cydymiaith in the Chrome browser.
2) From the Home page, click on the Posts navbar item.
3) On the Posts page, click 'Log In To Make Post' button. The user should be redirected to the Log In page.
4) On the Log In page, click 'Register here'. The user should be sent to the Register page.
5) Click 'Log In' from the navbar. The user should navigate to the Log In page.
6) Click 'Register' from the navbar. The user should navigate to the Register page.

Test result: Pass

#### Visibility

1) The navbar should contain the following links - Home, Posts, Log In, Register.
2) Navigate back to the Posts page. Check that only one filter selector (category) is visible. 
3) On the posts that are displayed, there should be no links to 'edit' or 'delete' posts.
4) Look for a post with at least one comment. Click the comments link. The user should be directed to a page that shows the comments on the post.
5) Check that on the comment(s), there are no links for 'Edit' or 'Delete'.
6) Try to add a comment. The user should be redirected to the Log In page, and a flash message should appear saying 'Please log in to access this page.'

Test result: Pass

### Student Role

Feature abilities and limitations are dependent on the user's role. I will start with the Student role.

#### Registration 

1) Navigate to cydymiaith in the Chrome browser, and click on the 'Register' navbar option.
2)  For the following form fields, enter these details.
  - Email: 'testuser1@abc.com'
  - Username: 'testuser1'
  - Password: 'testuser1'
3) If the values pass form validation (tested in the 'Defensive Programming Testing' section below), then upon clicking 'Register' the user should be redirected to the user's new profile page, that displays the username, 'Role: Student' and a flash message - "Registration Successful!".
4) The navbar menu items should have changed from 'Home, Posts, Log In, Register' to 'Home, Posts, Profile, Log Out'.

Test result: Pass

#### Log Out

1) Having registered an account, click the 'Log Out' navbar option.
2) The user should be redirected to the Log In page, with a flash message saying 'Logged Out'.
3) The navbar menu items should be 'Home, Posts, Log In, Register'.

Test result: Pass

#### Log In

1) Having logged out and on the Log In page, enter username (testuser1) and password (testuser1).
2) The user should be redirected to the user's profile page, with a flash message saying "Croeso, testuser1".

Test result: Pass

#### Post Creation

1) Having logged in, navigate to Posts. Beneath the Posts title, the button should say 'Make Post'.
2) Click 'Make Post'. The user should be redirected to the Make Post page.
3) Fill in form details such as:
- Category: Question
- All/Group: All
- Title: "Student functionality test"
- Description: "testing"
4) Press the Submit button. The user should be redirected to the Posts page, with a flash message saying "Post Published".
5) Check that:
- The most recent post at the top matches the above details. 
- The post should note how long ago the post was made when page was loaded.
- The post should have 0 Comments. 
- Unlike other posts, there should be 'Edit' and 'Delete' links visible for the created post.

Test result: Pass

#### Post Updating

1) On the created post ('Student functionality test'), click 'Edit'. The user should be redirected to the Edit Post page.
2) Check that the input fields display the current values:
- Category: Question
- For All or Group?: All
- Title: "Student functionality test"
- Description: "testing"
3) Change the values to the following and press 'Submit':
- Category: Diary Entry
- For All or Group?: All
- Title: "Student post edit test"
- Description: "edit testing"
4) The user should be redirected to the Posts page and there should be a flash message saying "Post Updated"
5) Check that the edited post displays the updated details.

Test result: Pass

#### Post Deletion

1) On the above post titled "Student post edit test", click 'Delete'. A modal should appear asking to either 'Cancel' or 'Confirm'. 
2) Click 'Cancel'. The modal should disappear having made no change.
3) Click 'Delete' again, and then 'Confirm'. The post should be deleted, and a flash message should say 'Post Deleted'.

Test result: Pass

#### Post Filtering by Category

We will test group filtering later.

1) If there are not multiple posts visible on the Posts page already, create some more test posts with differing categories.
2) From the Category drop down menu, select the first menu item, and press 'Filter'. The page should reload and only display posts of that category or no posts. The Category filter should also display the selected category.
3) Repeat for all category menu items.
4) Having tested each category, filter for 'All Categories'. All posts should now be visible to the user.

Test result: Pass

#### Comment Creation

1) Create a post with the following details:
- Category: Other
- For All or Group?: All
- Title: "Comment CRUD testing"
- Description: "testing"
2) On the post, click the 'Comments' link. The user should be directed to a page displaying the post with a comment box beneath.
3) In the comment box, type in "Comment creation test" and press 'Submit'. Check the following:
- The page should reload
- a flash message "Comment Added" should display
-  the new comment should be visible beneath the comment box
- the post's Comments number should have updated from 'O Comments' to '1 Comments'

Test result: Pass

#### Comment Editing

1) On the comments page for the 'Comment CRUD testing' post, click on the 'Edit' link for the new comment. The user should be taken to a page with an 'Edit Comment' text box that's populated with the previous comment.
2) Edit the comment to 'Comment edit test'. Press 'Save'.
3) Check that:
- The user is taken back to the comments page for the post
- A flash message reads 'Comment Edited'
- The comment text shows as 'Comment edit test'

Test result: Pass

#### Comment Deletion

1) On the comment, click the 'Delete' link. A modal should appear asking to 'Cancel' or 'Confirm'. 
2) Click 'Cancel'. The modal should disappear and nothing should have changed.
3) Click 'Delete' again, and then 'Confirm' on the modal.
4) Check the following:
- A flash message displays 'Comment Deleted'
- The number of comments should have changed to '0 Comments'
- The comment has been deleted

Test result: Pass

#### Profile Editing

1) Click the 'Profile' navbar option
2) On the profile, click 'Edit Profile'
3) Change the values to the following and press 'Save'
- Email: testuser1@abcd.com
- Level: Blasu
- Provider: Caerdydd / Cardiff
- Location: Abertawe
- Bio: "Hello world!"
4) Check that:
- the user is taken back to the profile page
- a flash message displays 'Profile Updated'
- the profile information has been updated
5) Click 'Edit Profile' again. On the Edit Profile page check that the input fields are populated with the current values.
6) Change the email address to one that you have access to in order to test password reset functionality in the next section. Click 'Save'.

Test result: Pass

#### Password Reset

1) On the Profile page, check that your email is set to the profile.
2) Click 'Reset Password'. A flash message should display "A confirmation email has been sent".
3) Find the email from cydymiaith@gmail.com in your inbox with the subject 'Password Reset Request'.
4) Open the email and click the link. The user should be taken to Cydymiaith's Reset Password page.
5) Enter the Email and New Password, and click 'Reset Password'. The user should be sent back to the profile page and a flash message should display "Your password has been reset".
6) Log out and log back in with the new password. Log in should succeed.

Test result: Pass

#### Profile Deletion

This test is more involved as it requires a bit of set up to fully test the full deletion cascade of all the comments the user has made, the posts the user has made, and all comments associated with those posts.

Set up

1) As testuser1, add a comment ('testuser1 deletion cascade test') to testuser1's post titled 'Comment CRUD testing'.
2) Log Out and Register a new profile of username 'testuser2', password 'testuser2'.
3) Create a post titled 'profile deletion cascade test'
4) Log Out and Log In as testuser1.
5) Find the post 'profile deletion cascade test' and add a comment.

Test

6) On testuser1's profile page, click 'Delete Profile'. A modal asking the user to 'Cancel' or 'Confirm' should appear.
7) Click 'Cancel'. The modal should disappear.
8) Click 'Delete Profile' again, and then 'Confirm'.
9) The user should be redirected to the Log In page and a flash message should display 'Account Deleted'.
10) Navigate to the Posts page. Check that:
- there are no posts by testuser1
- testuser1's comment on testuser2's post titled 'profile deletion cascade test' and check that there are no comments by testuser1.
11) Navigate to the Log In page and attempt to log in with testuser1's details. The page should refresh and flash a message 'Incorrect username and/or password'.

Test result: Pass

### Tutor Role

The Tutor role has all the abilities of the Student role plus more, which we will test below.

Using an Admin profile, I will set testuser2's role as 'Tutor' for the following tests. I will also create a new Student profile by registering an account using the following details:
- Email: testuser3@abc.com
- Username: testuser3
- Password: testuser3

#### Visibility

1) Log in as testuser2 and on the profile page, check that the role is set to 'Tutor'.
2) Check that the following navbar options are: Home, Posts, Profile, Users, Groups, Log Out
3) Navigate to the Users page. Check that at the bottom of each user card, only two links are visible: 'View Profile' and 'Add to Class'.

Test result: Pass

#### User Filtering

1) Set profile details for testuser2 to filter by.
2) On the Users page, filter by Level. Only users of that level should be visible, or no users at all.
3) Repeat for each level.
4) Set Level back to 'All' and repeat steps 2 and 3 but for Provider.
5) Reset Provider to 'All'.
6) Filter users by testuser2's Username, Email and Location, clearing the filter between each one. The filters are currently case sensitive.
7) The filter fields should remember filter settings. 

Test result: Pass

#### Group Creation

1) Navigate to the Groups page. There should be no groups currently visible.
2) Click 'Add Group'. The user should be taken to the Add Group page.
3) Fill the form using the following details:
- Provider: Y Fro / The Vale
- Level: Mynediad
- Year: 2024
- Weekday: Monday
4) The user should be redirected back to the Groups page, a flash message should display "Group Created" and the created group should be visible.

Test result: Pass

#### Group Editing

1) On the Groups page, click 'Edit Group' for the newly created group.
2) The user should be taken to the Edit Group page. Check that the form displays the current values. Change the values to the following:
- Provider: Gwent
- Level: Sylfaen
- Year: 2025
- Weekday: Tuesday
3) Click 'Submit'. The user should be taken back to the Groups page. A flash message should display 'Group Edited', and the details for the group should have changed accordingly.

Test result: Pass

#### Adding Students to a Group

1) Navigate to the Users page.
2) Find the profile card for testuser3.
3) Click 'Add to Class'. A modal should appear asking the user to choose a group, and there should appear an entry for the group 'Sylfaen, Tuesday, 2025'.
4) Press 'Cancel'. The modal should disappear.
5) Press 'Add to Class' again. This time select the radio button for the group and press 'Confirm'. The user should be redirected to the Groups page and a flash message should display "Student Added".
6) Click on the 'Student List' dropdown. testuser3 should be listed.

Test result: Pass

#### Assigning a post to a group

1) Create a new post with the following values:
- Category: Announcement
- For All or Group?: Tuesday, Gwent, Sylfaen
- Title: Post filtering by group test
- Description: abc
2) On the Posts page, select the group 'Tuesday, Gwent, Sylfaen' from the group filter dropdown and click 'Filter'. The post titled 'Post filtering by group test' should be visible.
3) Check that the selected group is still visible in the filter.

Test result: Pass

#### Student ability to filter posts by group

1) Log in as testuser3.
2) On the Posts page, in the group filter, select the group 'Tuesday, Gwent, Sylfaen' and click 'Filter'.
3) The post titled 'Post filtering by group test' should be visible.

Test result: Pass

#### Removing Students from a Group

1) Log back in as testuser2.
2) Navigate to the Groups page.
3) Open the Student List, and click the 'Remove' link for testuser3. A modal should appear.
4) Click 'Cancel'. The modal should disappear.
5) Click 'Remove' again, and then 'Confirm'. A flash message should display "Student Removed".
6) Check that testuser3 has been removed from the Student List.

Test result: Pass

#### Group Deletion

1) On the Groups page, click 'Delete Group' for the group. A modal should appear.
2) Click 'Cancel'. The modal should disappear.
3) Click 'Delete Group' again and then 'Confirm'.
4) Check that: 
- the user is redirected to the Groups page
- a flash message displays "Group Deleted"
- the group no longer appears

Test result: Pass

### Admin Role

The Admin role has all the abilities of the Tutor role plus more, which we will test below.




## Defensive Programming Testing

[Back to top](#cydymiaith-testing-documentation)



## Responsiveness Testing

[Back to top](#cydymiaith-testing-documentation)



## Browser Testing

[Back to top](#cydymiaith-testing-documentation)



## Automated Testing

[Back to top](#cydymiaith-testing-documentation)



### HTML Validation

### CSS Validation

### Python Validation

### WAVE

### Lighthouse

## Bugs

- Getting edit question form to remember associated group - I was having trouble handling id vs ObjectId - I consulted GPT4o who advised me how to use jinja filters properly, such as 

` {% if group._id|string == question.group_id|string %}`

and this equates the types making them comparable.

