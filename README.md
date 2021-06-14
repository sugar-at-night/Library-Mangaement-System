# ReadMe
This is a little project for a small community library.

## Table of Contents
- [Background](#background)
- [Install](#install)
- [Usage](#usage)
    - [Public Interface](#Public-Interface)
    - [Staff Interface](#Staff-Interface)


## Background
A small community library with a few branches has approached me to develop a system that will 
allow it to manage members (borrowers) and book loans that they make.
There should be two interfaces with functional requirements:
1. [**The public interface**](#Public-Interface), not requiring any identifying information to be entered, should allow borrowers to search the catalogue to find out which books are available, if they are on loan or not (and if they are when they are due back)
2. [**The staff interface**](#Staff-Interface) is focused on library staff, allowing them to search the book, issue books to borrowers and return books that have been on loan, to check overdue loans, to view borrower's information and record.
3. **The Database** is given,can be seen in folder "MySQL Database". Here is a data model I made to help understanding the SQL in my project.
<img src="README-img/MySQL-DataModel.png" alt="MySQL-DataModel" width="650"/><br/>

## Install
This application is based on the MySQL, Python, Flask.

1. Clone the repository. 
2. Run the requirements.txt to build a virtual envirnonment.
3. Build your database on your own server
You can use the scripts inside folder "MySQL Database" to build your database on your own server(AWS or SQL Sever, anywherer you prefer), and then fill in the connect.example.py.
*I removed my connection.py due to the protection of my sensitive data, but you can fill in yours to connect to the database.*
4. Then run the app.py. 
5. Now, you can enter the system through http://127.0.0.1:5000/



### Public Interface
**Route:** 
"/"

**Function:**<br/>
Fuzzy search a book by title and/or author. <br/>
See the availability of a book at each branch, if it is on loan, the due date will be displayed.<br/>
<img src="README-img/public-interface_search.png" alt="public-interface:search a book" width="650"/>
<img src="README-img/public-interface_searchresult.png" alt="public-interface:search result" width="650"/><br/>

**Assumptions and Design decisions:**<br/>
I make the public interface a page with function. They can directly do the search on this page following the lead, and the result will appear on this route too.<br/>
The search result is spilted into two parts.<br/>
For most users, the first part "Search Result" will suffice. It's clear to show whether this book is available or not, if not, they can go to other branch where this book is available.<br/>
If they insist on this book, then they scroll down to the second part "See all the on loan records". <br/>
The second part is designed especially for the borrowers who have specific needs, like "I want to borrow several copies from the same branch, one for myself, others for my mates in reading club." They want to know when all the copies are available. It's no help only tell them "The Lost Tribe is available in this branch, and since one is available, I can't tell you the due date of other 3 which has been borrowed."<br/>

**Screenshots for different situations:**<br/>
Normal situation has been showed in above screenshots with two parts.<br/>
If all the copies of this book are available at all branches, then the second part won't appear. <br/>
<img src="README-img/public-interface_all_available.png" alt="public-interface:books are available anywhere" width="650"/><br/>
For users who are not clearly about what they want, just like i said in the public interface,"Input nothing to see everything", just click the button, then view all the catalouge and records to  see what wanted.<br/>
<img src="README-img/public-interface_everything.png" alt="public-interface:show everything" width="650"/><br/>
Of cousre, ther is also a situation to tell "no record". <br/>
I didn't use a custom error page here, because maybe we do not have that book in our library. It is not supposed to be called as the error. Therefore, this page is written in html,if no search result, this section appear.<br/>
<img src="README-img/public-interface_no_record.png" alt="public-interface:no record here" width="650"/><br/>


### Staff Interface
**Route:**
"/staff"

**Function:**
- [search a book](#search-a-book)
- [view the record of a borrower](#view-the-record-of-a-borrower)
- [issue a book](#issue-a-book)
- [return a book](#return-a-book)
- [display overdue books and their borrowers](#display-overdue-books-and-their-borrowers)
    
**Assumptions and Design decisions:**<br/>
As the design of public page, I made staff page the same. <br/>
Staff can do all their work on this page.<br/>
<img src="README-img/staff-interface.png" alt="staff-interface" width="650"/><br/>


#### Search a book
This function is samed as the one in public interface, they both return to the "/BookResult" to view the result.<br/>
From the business view, the staff mostly use this function to do the inventory verification, which means the staff need to see all the books at the same time. And they may need to help the borrower to check if the book is available, so the fuzzy research is still needed.<br/>
Since the same function can meet both needs for staff and borrowers, so i just recall it here.<br/>


#### View the record of a borrower
This function is to view the record of a borrower.<br/>
This business scenario often happens when someone want to borrow a book, then the librarian take his card and the book he want to borrow. Then the librarian input the card ID to see if this borrower are allowed to borrow the book, maybe he has overdue loans. <br/>
Or the borrower ask to have a picture of his loans, in this kind of situation, the borrower may not bring the card with him and he can't remember the card ID. One must tell his name correctly to prove that he is a member here, the librian also need to ask for the telephone or address for further check to decide whether to tell him the details of the debt. <br/>
Therefore, this function asks a ID or a name, which are supposed to be precisely correct. And the result data includes the items like personal inforamtion and their loans, especially the status of their loans.<br/>
The result will be displayed at the route "/staff/BorrowerRecord"<br/>

If sucessfully done, then the record will be displayed like below screenshot.<br/>
<img src="README-img/staff-interface_borrowerrecord.png" alt="staff-interface:view the record of a borrower" width="650"/><br/>
If failed, then the page will display the hints.<br/>
<img src="README-img/staff-interface_failed.png" alt="staff-interface:failed to do" width="650"/><br/>

#### Issue a book
This function requires Book ID, Branch ID, Card ID at same time. <br/>
Normally, the Book ID and Branch ID can be found on the cover of the book. And when borrower want to borrow a book, he need to pass the book and his card to the librarian so the librarian can get the card ID too.<br/>
According to the real business, all the book is issued by current date, and the period is 28 days. So don't need to input these things, it's been set already.<br/>
After issuing a book, record of this borrower on this book which has been lent today from this branch will be displayed for the librarian to check again.<br/>
The result will be displayed at the route "/staff/IssueABook"<br/>

If sucessfully done, then the record will be displayed like below screenshot.<br/>
<img src="README-img/staff-interface_issueabook.png" alt="staff-interface:issue a book sucessfully" width="650"/><br/>
If failed, then the page will display the hints.<br/>
<img src="README-img/staff-interface_failed.png" alt="staff-interface:failed to do" width="650"/><br/>

#### Return a book
This function requires Book ID, Branch ID, Card ID at same time as well. <br/>
Normally, the Book ID and Branch ID can be found on the cover of the book. And when borrower want to return a book, he need to pass the book and his card to the librarian so the librarian can get the card ID too.<br/>
After doing this, record of this borrower on this book from this branch which has been returned will be displayed for the librarian to check again.<br/>
The result will be displayed at the route "/staff/ReturnABook"<br/>

If sucessfully done, then the record will be displayed like below screenshot.<br/>
<img src="README-img/staff-interface_returnabook.png" alt="staff-interface:return a book sucessfully" width="650"/><br/>
If failed, then the page will show the hint.<br/>
<img src="README-img/staff-interface_failed.png" alt="staff-interface:failed to do" width="650"/><br/>


#### Display overdue books and their borrowers
The duedate is yesterday and the book is not returned can be regarded as overdue. <br/>
Take the same name of books and the same name of borrowers into consideration, the author name, branch name, the borrowers' card ID are included. <br/>
The result will be displayed at the route "/staff/Overdue" <br/>

Following this principle, it can automatically generate a list if there are overdue loans. <br/>
<img src="README-img/staff-interface_overdue.png" alt="staff-interface:overdue loans" width="650"/><br/>
If there is no, than the good news will be displayed. <br/>
<img src="README-img/staff-interface_nooverduetoday.png" alt="staff-interface:no overdue loans so far" width="650"/><br/>
