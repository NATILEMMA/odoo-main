
  
# Membership Custom Module

  

Membership custom module will create custom changes to the already existing membership module based on the client's request.

  

### Table of contents

  

----

<div align="center">

  

[Features](#features)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Installation](#installation)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Configuration](#configuration)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Usage](#usage)

  

</div>

  

----

  

<h2 id="features">Features</h2>

  

- It will add new demographic fields to the members form.

- Users will be able to edit their profile, add complaint ,see the status of their complaints and attach files. 

- There will be user's who handle membership. We used 4 basic ones. Adimn, Manager, Complaint Handler and Agent.

- Only employees of a department will be able to see and handle their own members belonging to that same department.

- There will be employees who handle complaints and send report to a member.

- Members will get their own ID and PDF format of their complaints.


  

<h2 id="installation">Installation</h2>

  

No new Installation required.

  

<h2 id="configuration">Configuration</h2>


To configure this module you'll need:

- To create users who are going to be an employees.

      1. Settings >> Manage Users >>  Create

        * You can create as many users you want. Preferably add 4 to test.

        * Member Handlers section of the user must be filled out as either Administrator, Manager, Complaint Management or Agent

        * Save the new User and create an employee.

      2. Go to the employee module and fill out all the details

        * Make sure each department has a manager, who is also an employee. 


 - To create Complaint Category

 
       1. This section will only be edited by a user who is a Manager or Adminstrator

         * Members >> Complaint >> Complaint Categories
 
         * Add a complaint type, the department it concerns and the employee of that department to whom the complaint concerns.

  

- To create Membership Product

  
      1. This section will only be edited by a user who is a Manager or Administrator

        * Members >> Configuration >> Membership Product

        * Make sure to add the price of the product

  

- To create Attachment Types

  

      1. This section will only be edited by a user who is a Manager or Adminstrator

        * Members >> Configuration >> Attachment Types

        * Make sure to add the names of the different attachment types you want the Member to submit. Eg. National ID, Driver's License
  

<h2 id="usage">Usage</h2>

  

1. As a member go to website: 

    * Sign in
    * Fill out your information
    * Add, Update, Check Status and Download Reports complaints
    * Add, Update Attachment.

2. As an Agent: 

    * You can create a profile for members who aren't able to do so on the website.
    * You can fill out informations, add, update complaints, add, edit attachment and assign membership.
    
    Agent is also an employee and can check the status of complaints for members.

3. As a Complaint Manager:

    * They are able to edit and review complaints that they are assigned to handle.
    * They can change status of complaint.
    * Send email regarding the status of complaint
    * Write review and send email of the review to employee.
   
    As an employee handling members, They can also see profiles of members.

 4. As a Manager:

    * You will create complaint categories, attachment types, membership products.
    * You will also see member's profile, read and see the status of complaints.

   
 5. As an Administrator:

    * You will be able to do any thing the other employees can and can't do.
    * <strong>Preferably use this user to test the module.</strong>
