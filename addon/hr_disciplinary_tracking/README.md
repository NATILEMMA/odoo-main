
  
# Disciplinary Tracking Custom Module

  

Disciplinary Tracking Custom module will create custom changes to the already existing Open HRMS Disciplinary Tracking module based on the client's request.

  
  

----

<div align="center">

  

[Features](#features)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Depends](#depends)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Installation](#installation)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Configuration](#configuration)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Usage](#usage)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Bug Tracker](#bugtracker)&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;[Author](#author)

  

</div>

  

----

  

<h2 id="features">Features</h2>

  

- Administrators will be able to add Disciplinary and Action Category.

- Administrators will add Complaint Assessor for Department.

- Employees will be able to add complaint inside complaint page inside "My Profile".

- Administrators will be able to send complaint to accused Employees

- Employees will give justification to the complaint that they have been accused in.

- Administrators will the send to the Employee, that made the complaint, the action that was taken and detailed explanation of the action

- Employees will also be able to make complaint about department

- Administrators that handle complaint about department will answer report to employees



<h2 id="depends">Depends</h2>


[oh_employee_creation_from_user] addon Open HRMS
[mail] addon Odoo
  

<h2 id="installation">Installation</h2>

  

No new Installation required.

  

<h2 id="configuration">Configuration</h2>


To configure this module you'll need:

- To create users who are going to be an employees.

      1. Settings >> Manage Users >>  Create

        * You can create as many users you want. Preferably add 3 to test.

        * User can be Administrator or Officer.


      2. Go to the employee module and fill out all the details

        * Add department to the employee record.
        
        * Add to the Departments a Complaint Assesor, who is also Administrator.


 - To create Discipline Category

 
       1. This section will only be viewed and edited by a user who is an Adminstrator.

         * Employee >> Disciplinary Actions >> Discipline Category
 
         * Add a name, code and action
         
         
 - To create Discipline Action

 
       1. This section will only be viewed and edited by a user who is an Adminstrator.

         * Employee >> Disciplinary Actions >> Discipline Action
 
         * Add a name and code.

  

  

<h2 id="usage">Usage</h2>

  

1. As a victim employee: 

    * Click on your name on the top right corner
    * Go To "My Profile"
    * Go To "Complaint" page
    * Add Complaint, after saving it will be a draft, so it can be edited. "Send For Approval" will send it to disciplinary action or complaint assesor based on the mode.


2. As an Admistrator who handles Disciplinary Action: 

    * You can send out complaint to employees who have been accused
    * You can also receive explantion from accused employees and send a the action taken and report to the victim employee who wrote the complaint.
    

3. As an accused employee: 

    * Click on your name on the top right corner
    * Go To "My Profile"
    * Click on Disciplinary Count on the top right of the profile form, It will either be 0, if you haven't been accused or More than 1.
    * You can read the complaint report and given your explanation and send it.
    

3. As an Admistrator who handles Departmental Complaints:

    * You can receive complaints that are about your department.
    * You can receive complaints from employees and write report to them.
   


4. As an employee who made a complaint:

    * You will receive complaint report about the accused department.
    
    
    
<h2 id="bugtracker">Bug Tracker</h2>


Bugs are tracked on GitHub Issues. In case of trouble, please check there if your issue has already been reported.



<h2 id="author">Author</h2>
  
  
Developer: Ajmal J K @ cybrosys