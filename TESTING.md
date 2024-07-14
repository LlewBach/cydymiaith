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

Feature abilities and limitations are dependent on the user's role. I will start with the Student role.

### Student Role

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

