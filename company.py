from flask import Flask, render_template, request, redirect, url_for, flash
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)
app.secret_key = "Company"

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

output = {}
table = 'Company', 'Job', 'StudentApplication'

# routes
@app.route("/Company")
def indexCompany():
    return render_template('index.html')

# Company
@app.route("/Registration", methods=['GET', 'POST'])
def registration():
    return render_template('Registration.html')

@app.route("/RegistrationProcess", methods=['POST'])
def registrationProcess():
    company_name = request.form['name']
    company_des = request.form['description']
    contact = request.form['contactNum']
    email = request.form['email']
    work_des = request.form['workDes']
    entry_req = request.form['entryReq']
    image = request.files['company_image_file']
    
    insert_sql = "INSERT INTO Company VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    
    if image.filename == "":
        return "Please select a file"
    
    try:
        cursor.execute(insert_sql, (company_name, company_des, contact, email, work_des, entry_req))
        db_conn.commit()
        
        # Uplaod image file in S3 #
        company_image_file_name_in_s3 = "company-name-" + str(company_name) + "_image_file"
        s3 = boto3.resource('s3')
        
        try:
            print("Data inserted in MariaDB RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=company_image_file_name_in_s3, Body=image)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                company_image_file_name_in_s3)

        except Exception as e:
            return str(e)
        
    finally:
        flash('Company Registered Successfully')
        cursor.close()

    return redirect(url_for('Jobs'))

# Job
@app.route("/Jobs", methods=['GET'])
def Jobs():
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM Job')
    data = cursor.fetchall()
    cursor.close()
    
    return render_template('Jobs.html', job = data)

@app.route("/CreateJobs", methods=['GET', 'POST'])
def CreateJobs():
    return render_template('CreateJobs.html')

@app.route("/Jobs", methods=['POST'])
def addJob():
    if request.method == 'POST':
        job_title = request.form['jobTitle']
        job_location = request.form['jobLocation']
        min_req = request.form['minReq']
        
        # Initialize the cursor
        cursor = db_conn.cursor()
        
        try:         
            insert_sql = "INSERT INTO Job (job_title, job_location, min_req) VALUES (%s, %s, %s)"
            cursor.execute(insert_sql, (job_title, job_location, min_req))
            db_conn.commit()
            # Get the auto-generated job_id
            auto_generated_job_id = cursor.lastrowid
        finally:
            cursor.close()
            return redirect(url_for('Jobs'))
        
    # Handle the GET request here
    return render_template('AddJob.html')

#
@app.route("/edit/<int:id>", methods=['POST', 'GET'])
def editJob(id):
    cursor = db_conn.cursor()
    if request.method == 'GET':
            # Fetch the job details from the database based on the provided 'id'
            cursor.execute('SELECT * FROM Job WHERE jobID = %s', (id))
            job = cursor.fetchone()

            if job:
                # Render the edit job form with the fetched job details
                return render_template('EditJob.html', job=job, id=id)

    elif request.method == 'POST':
        # Update the job details in the database based on the form submission
        job_id = request.form['jobID']
        job_title = request.form['jobTitle']
        job_location = request.form['jobLocation']
        min_req = request.form['minReq']

        cursor.execute('UPDATE Job SET jobTitle = %s, jobLocation = %s, minReq = %s WHERE jobID = %s',
                    (job_title, job_location, min_req, id))
        db_conn.commit()

        cursor.close()

        # Redirect to the jobs page after editing
        return redirect(url_for('Jobs'))

#
@app.route("/delete/<int:id>", methods=['GET'])
def deleteJob(id):
    cursor = db_conn.cursor()

    # Delete the job from the database based on the provided 'id'
    cursor.execute("DELETE FROM Job WHERE jobID = %s", (id))
    flash('Job Deleted Successfully')
    db_conn.commit()
    cursor.close()

    # Redirect to the jobs page after deleting
    return redirect(url_for('Jobs'))

# Application
@app.route("/Application", methods=['GET'])
def Application():
    cursor = db_conn.cursor()
    status_value = 'pending'
    cursor.execute('SELECT * FROM StudentApplication WHERE appStatus = %s', status_value)
    data = cursor.fetchall()
    cursor.close()
    
    return render_template('Application.html', application = data)

@app.route("/ApplicationStatus", methods=['GET'])
def ApplicationStatus():
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM StudentApplication')
    data = cursor.fetchall()
    cursor.close()
    
    return render_template('ApplicationStatus.html', application = data)

@app.route('/rejectStudentApplication/<string:id>', methods = ['POST', 'GET'])
def rejectStudentApplication(id):
    cursor = db_conn.cursor()
    status_change = 'rejected'
    cursor.execute('UPDATE StudentApplication SET appStatus = %s WHERE studentID = %s', (status_change, id))
    flash('Student Application Rejected Successfully')
    db_conn.commit() 
    # cursor.close()
    return redirect(url_for('Application'))

        

@app.route('/approveStudentApplication/<string:id>', methods = ['POST', 'GET'])
def approveStudentApplication(id):
    cursor = db_conn.cursor()
    status_change = 'approved'
    cursor.execute('UPDATE StudentApplication SET appStatus = %s WHERE studentID = %s', (status_change, id))
    flash('Student Application Approved Successfully', 'success')
    db_conn.commit() 
    # cursor.close()
    return redirect(url_for('Application'))

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)