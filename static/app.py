from logging import NullHandler
from re import S
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import mysql.connector
import connect
connection = None
dbconn = None

app = Flask(__name__)

# connect to database
def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser,
                                             password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn

# public interface 
@app.route("/")
def public_interface():
    return render_template("public.html")

# search a book
@app.route("/BookResult", methods=['GET', 'POST'])
def search_a_book():
    if request.method == 'POST':
        title = request.form.get('searchTitle')
        author = request.form.get('searchAuthor')
        input_title = '%' + title + '%'
        input_author = '%' + author + '%'
        cur = getCursor()
        # fuzzy search a book by title and/or author
        # see the availability of a book at each branch.
        cur.execute("select distinct Book.Title, Author.AuthorName, Library_Branch.BranchName, "
                    "Book_Copies.No_Of_Copies, "
                    "count(case when Book_Loans.returned=0 then 1 else null end) as 'No_Of_Copies_On_Loan', "
                    "if(Book_Copies.No_Of_Copies > count(case when Book_Loans.returned=0 then 1 else null end), 'available', 'not available now') as 'Availablity' "
                    "from Book_Loans "
                    "right join Book_Copies on Book_Loans.Bookid=Book_Copies.BookId and Book_Loans.BranchId=Book_Copies.BranchId "
                    "inner join Book on Book_Copies.BookId=Book.Bookid "
                    "inner join Author on Book.Author=Author.AuthorId "
                    "inner join Library_Branch on Book_Copies.BranchId=Library_Branch.BranchId "
                    "where Book.Title like %s and Author.AuthorName like %s"
                    "group by Book.Title, Author.AuthorName, Library_Branch.BranchName; ", (input_title, input_author, ))
        select_result = cur.fetchall()
        column_names = ["Book Title", "Author Name", "Branch Name",
                        "Total Copies", "Total On Loan", "Availablity"]
        #For user's further information, all the due date record will be displayed.
        cur.execute("SELECT Book.Title, Author.AuthorName, Library_Branch.BranchName, Book_Copies.No_Of_Copies, if(Book_Copies.No_Of_Copies=0, 0, 1) as 'one be borrowed', Book_Loans.DueDate "
                    "FROM Book_Loans "
                    "left JOIN Book_Copies ON Book_Loans.Bookid=Book_Copies.BookId AND Book_Loans.BranchId=Book_Copies.BranchId "
                    "inner JOIN Book ON Book_Copies.BookId=Book.Bookid "
                    "inner JOIN Author ON Book.Author=Author.AuthorId "
                    "inner JOIN Library_Branch ON Book_Copies.BranchId=Library_Branch.BranchId "
                    "where Book.Title like %s AND Author.AuthorName like %s AND Book_Loans.returned=0;", (input_title, input_author, ))
        select_result_detail = cur.fetchall()
        column_names_detail = ["Book Title", "Author Name", "Branch Name",
                               "Total Copies", "One On Loan", "DueDate"]
        return render_template('bookresult.html', dbresult=select_result, dbcols=column_names, dbresult_detail=select_result_detail, dbcols_detail=column_names_detail)
    else:
        return render_template('public.html')


# the staff interface
@app.route("/staff")
def staff_interface():
    return render_template("staff.html")


# view the record of a borrower
@app.route("/staff/BorrowerRecord", methods=['GET', 'POST'])
def borrower_record():
    if request.method == 'POST':
        borrowername = request.form.get('borrowerName')
        borrowerid = request.form.get('borrowerCardNo')
        cur = getCursor()
        # View the record of a borrower, searching by name or library card id
        cur.execute(
            "SELECT Borrower.* , Book.Title, Author.AuthorName, Library_Branch.BranchName, Book_Loans.DateOut, Book_Loans.DueDate, if(Book_Loans.returned=1, 'returned', 'not returned') "
            "FROM Borrower "
            "inner JOIN Book_Loans ON Borrower.CardNo=Book_Loans.CardNo "
            "inner JOIN Book_Copies ON Book_Loans.Bookid=Book_Copies.BookId AND Book_Loans.BranchId=Book_Copies.BranchId "
            "inner JOIN Book ON Book_Copies.BookId=Book.Bookid "
            "inner JOIN Author ON Book.Author=Author.AuthorId "
            "inner JOIN Library_Branch ON Book_Copies.BranchId=Library_Branch.BranchId "
            "WHERE Borrower.CardNo=%s OR Borrower.Name=%s;", (borrowerid, borrowername, )
        )
        select_result = cur.fetchall()
        column_names = ["Borrower CardNO", "Name", "Address", "Phone", "Book Title", "Author Name", "Branch Name",
                        "Date Out", "Due Date", "Status"]
        # add error handling here, if nothing be selected then raise an errror                       
        if select_result == []:
            return render_template('500.html') 
        else:
            return render_template("borrowerrecord.html", dbresult=select_result, dbcols=column_names)  
    else:
        return render_template("staff.html")

# issue a book
@ app.route("/staff/IssueABook", methods=['GET', 'POST'])
def issue_a_book():
    if request.method == 'POST':
        bookid = request.form.get('bookID')
        branchid = request.form.get('branchID')
        borrowerid = request.form.get('borrowerCardNo')
        cur = getCursor()
        #  Issue a book to a borrower. (28 day issue period)
        cur.execute("INSERT INTO Book_Loans(BookId, BranchId, CardNo, DateOut, DueDate, returned)"
                    "VALUES (%s, %s, %s, CURRENT_DATE(), DATE_ADD(CURRENT_DATE(),INTERVAL 28 DAY), 0);", (bookid, branchid, borrowerid, ))
        # display the record for check
        cur.execute("SELECT Borrower.* , Book.Title, Author.AuthorName, Library_Branch.BranchName, Book_Loans.DateOut, Book_Loans.DueDate, if(Book_Loans.returned=1, 'returned', 'not returned') "
                    "FROM Borrower "
                    "inner JOIN Book_Loans ON Borrower.CardNo=Book_Loans.CardNo "
                    "inner JOIN Book_Copies ON Book_Loans.Bookid=Book_Copies.BookId AND Book_Loans.BranchId=Book_Copies.BranchId "
                    "inner JOIN Book ON Book_Copies.BookId=Book.Bookid "
                    "inner JOIN Author ON Book.Author=Author.AuthorId "
                    "inner JOIN Library_Branch ON Book_Copies.BranchId=Library_Branch.BranchId "
                    "WHERE Book_Loans.BookId=%s AND Book_Loans.BranchId=%s AND Borrower.CardNo=%s And Book_Loans.DateOut=CURRENT_DATE();", (bookid, branchid, borrowerid, ))
        select_result = cur.fetchall()
        column_names = ["Borrower CardNo", "Name", "Address", "Phone", "Book Title", "Author Name", "Branch Name",
                        "Date Out", "Due Date", "Status"]
        # don't need to manually raise an error here
        # due to the foreign key constraint, it will automatically turn to a internal server error500
        # and to 500 error, there is a function to catch and handle
        return render_template("issue.html", dbresult=select_result, dbcols=column_names)
    else:
        return render_template("staff.html")

# return a book
@ app.route("/staff/ReturnABook", methods=['GET', 'POST'])
def return_a_book():
    if request.method == 'POST':
        bookid = request.form.get('bookID')
        branchid = request.form.get('branchID')
        borrowerid = request.form.get('borrowerCardNo')
        cur = getCursor()
        # Return a book that has been on loan
        cur.execute("UPDATE Book_Loans SET returned=1 "
                    "WHERE Book_Loans.returned=0 AND Book_Loans.BookId=%s AND Book_Loans.BranchId=%s AND Book_Loans.CardNo=%s;", (bookid, branchid, borrowerid, ))
        # display the record for check
        cur.execute("SELECT Borrower.* , Book.Title, Author.AuthorName, Library_Branch.BranchName, Book_Loans.DateOut, Book_Loans.DueDate, if(Book_Loans.returned=1, 'returned', 'not returned') "
                    "FROM Borrower "
                    "inner JOIN Book_Loans ON Borrower.CardNo=Book_Loans.CardNo "
                    "inner JOIN Book_Copies ON Book_Loans.Bookid=Book_Copies.BookId AND Book_Loans.BranchId=Book_Copies.BranchId "
                    "inner JOIN Book ON Book_Copies.BookId=Book.Bookid "
                    "inner JOIN Author ON Book.Author=Author.AuthorId "
                    "inner JOIN Library_Branch ON Book_Copies.BranchId=Library_Branch.BranchId "
                    "WHERE Book_Loans.BookId=%s AND Book_Loans.BranchId=%s AND Borrower.CardNo=%s;", (bookid, branchid, borrowerid, ))
        select_result = cur.fetchall()
        column_names = ["Borrower CardNo", "Name", "Address", "Phone", "Book Title", "Author Name", "Branch Name",
                        "Date Out", "Due Date", "Status"] 
        # add error handling here, if nothing be selected then raise an errror                       
        if select_result == []:
            return render_template('500.html') 
        else:
            return render_template("return.html", dbresult=select_result, dbcols=column_names)     
    else:
        return render_template("staff.html")


# Display a list of overdue books & their borrowers
@ app.route("/staff/Overdue")
def check_overdue():
    cur = getCursor()
    cur.execute("SELECT Book.Title, Author.AuthorName, Library_Branch.BranchName, Borrower.Name, Borrower.CardNo "
                "FROM Book_Loans "
                "INNER JOIN Library_Branch ON Book_Loans.BranchId=Library_Branch.BranchId "
                "INNER JOIN Book ON Book_Loans.BookId=Book.Bookid "
                "inner JOIN Author ON Book.Author=Author.AuthorId "
                "INNER JOIN Borrower ON Book_Loans.CardNo=Borrower.CardNo "
                "WHERE ( TO_DAYS(NOW( )) - TO_DAYS(Book_Loans.DueDate) >= 1 ) AND Book_Loans.returned=0;")
    select_result = cur.fetchall()
    column_names = ["Book Title", "Branch Name", "Author Name", "Borrower Name", "Borrower CardNo" ]
    return render_template("overdue.html", dbresult=select_result, dbcols=column_names)

# erorhandler for wrong url
@app.errorhandler(404)
def not_found_error(error):
    print(404)
    return render_template('404.html'),404

# erorhandler for internal server error and custom error
@app.errorhandler(500)
def internal_server_error(error):
    print(500)
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run()



