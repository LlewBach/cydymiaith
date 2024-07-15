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

### Unregistered Users

#### Navigation

1) Navigate to cydymiaith in the Chrome browser.
2) From the Home page, click on the Posts navbar item.
3) On the Posts page, click 'Log In To Ask Question' button. The user should be redirected to the Log In page.
4) On the Log In page, click 'Register here'. The user should be sent to the Register page.
5) Click 'Log In' from the navbar. The user should navigate to the Log In page.
6) Click 'Register' from the navbar. The user should navigate to the Register page.

#### Visibility

1) The navbar should contain the following links - Home, Posts, Log In, Register.
2) Navigate back to the Posts page. Check that only one filter selector (category) is visible. 
3) On the posts that are displayed, there should be no links to 'edit' or 'delete' posts.
4) Look for a post with at least one comment. Click the comments link. The user should be directed to a page that shows the comments on the post.
5) Check that on the comment(s), there are no links for 'Edit' or 'Delete'.
6) Try to add a comment. The user should be redirected to the Log In page, and a flash message should appear saying 'Please log in to access this page.'

### Student Role

Feature abilities and limitations are dependent on the user's role. I will start with the Student role.

#### Registration 

1) Navigate to cydymiaith in the Chrome browser, and click on the 'Register' navbar option.
2)  For the following form fields, enter these details.
  - Email: 'testuser1@abc.com'
  - Username: 'testuser1'
  - Password: 'testuser1'
3) If the values pass form validation (tested in the 'Defensive Programming Testing' section below), then upon clicking 'Register' the user should be redirected to the user's new profile page, that displays the username, 'Role: Student' and a flash message - "Registration Successful!".
4) The navbar menu items should have changed from 'Home, Posts, Log In, Register' to 'Home, Posts, Profile, Users, Log Out'.

#### Log Out

1) Having registered an account, click the 'Log Out' navbar option.
2) The user should be redirected to the Log In page, with a flash message saying 'Logged Out'.
3) The navbar menu items should be 'Home, Posts, Log In, Register'.

#### Log In

1) Having logged out and on the Log In page, enter username (testuser1) and password (testuser1).
2) The user should be redirected to the user's profile page, with a flash message saying "Croeso, testuser1".

#### Post Creation

1) Having logged in, navigate to Posts. Beneath the Posts title, the button should say 'Ask Question'.
2) Click 'Ask Question'. The user should be redirected to the Make Post page.
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

#### Post Deletion

1) On the above post titled "Student post edit test", click 'Delete'. A modal should appear asking to either 'Cancel' or 'Confirm'. 
2) Click 'Cancel'. The modal should disappear having made no change.
3) Click 'Delete' again, and then 'Confirm'. The post should be deleted, and a flash message should say 'Post Deleted'.

#### Post Filtering by Category

We will test group filtering later.

1) If there are not multiple posts visible on the Posts page already, create some more test posts with differing categories.
2) From the Category drop down menu, select the first menu item, and press 'Filter'. The page should reload and only display posts of that category or no posts. The Category filter should also display the selected category.
3) Repeat for all category menu items.
4) Having tested each category, filter for 'All Categories'. All posts should now be visible to the user.


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

