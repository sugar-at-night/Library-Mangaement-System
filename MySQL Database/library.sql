CREATE SCHEMA Library;

USE Library;

CREATE TABLE Publisher
(
Name varchar(50) PRIMARY KEY NOT NULL,
Address varchar(50),
Phone nchar(10)
);	

CREATE TABLE Author
(
AuthorId int NOT NULL PRIMARY KEY,
AuthorName varchar(50) NOT NULL
);	

CREATE TABLE Book
(
BookId int PRIMARY KEY NOT NULL,
Title varchar(50) NOT NULL,
PublisherName varchar(50) NOT NULL,
Author int NOT NULL,
FOREIGN KEY(PublisherName) REFERENCES Publisher(Name)
ON UPDATE CASCADE
ON DELETE CASCADE,
FOREIGN KEY(Author) REFERENCES Author(AuthorId)
ON UPDATE CASCADE
ON DELETE CASCADE
);	

CREATE TABLE Library_Branch
(
BranchId int PRIMARY KEY NOT NULL,
BranchName varchar(50) NOT NULL,
Address varchar(50)
);	

CREATE TABLE Borrower
(
CardNo int PRIMARY KEY NOT NULL,
Name varchar(50) NOT NULL,
Address varchar(50),
Phone nchar(10) 
);	


CREATE TABLE Book_Copies
(
BookId int NOT NULL,
BranchId int NOT NULL,
No_Of_Copies int NOT NULL,
FOREIGN KEY(BookId) REFERENCES Book(BookId)
ON UPDATE CASCADE
ON DELETE CASCADE,
FOREIGN KEY(BranchId) REFERENCES Library_Branch(BranchId)
ON UPDATE CASCADE
ON DELETE CASCADE
);



CREATE TABLE Book_Loans
(
BookId int NOT NULL,
BranchId int NOT NULL,
CardNo int NOT NULL,
DateOut date,
DueDate date,
returned tinyint(1),
FOREIGN KEY(BookId) REFERENCES Book(BookId)
ON UPDATE CASCADE
ON DELETE CASCADE,
FOREIGN KEY(BranchId) REFERENCES Library_Branch(BranchId)
ON UPDATE CASCADE
ON DELETE CASCADE,
FOREIGN KEY(CardNo) REFERENCES Borrower(CardNo)
ON UPDATE CASCADE
ON DELETE CASCADE
);	



  