# 💊 Medicine Reminder System

A web-based **Medicine Reminder System** developed using **Python Flask** that helps users manage their medicines and receive timely reminders. The application provides a simple and user-friendly interface for adding medicines, scheduling reminder times, and managing medication information.

## 🚀 Features

* 💊 Add medicine details
* ⏰ Set medicine reminder times
* 📋 View scheduled medicines
* ✏️ Update medicine information
* 🗑️ Delete medicine reminders
* 🔔 Receive medication reminders
* 📱 Responsive and user-friendly interface
* 🗄️ SQLite database for storing medicine information

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript

### Tools & Libraries

* Flask
* SQLite3
* Jinja2
* Gunicorn

## 📂 Project Structure

```text
medicine-reminder/
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── add_medicine.html
│   ├── edit_medicine.html
│   └── ...
│
├── app.py
├── database.db
├── requirements.txt
├── Procfile
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/medicine-reminder.git
```

### 2. Navigate to the Project Directory

```bash
cd medicine-reminder
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000/
```

## 💡 How It Works

1. Open the Medicine Reminder System.
2. Add the medicine name and required details.
3. Select the required reminder time.
4. Save the medicine information.
5. The medicine appears in the scheduled medicines list.
6. Users can edit or delete medicine reminders whenever required.
7. The system helps users keep track of their medication schedule.

## 🗄️ Database

The application uses **SQLite** as its database.

Medicine information can include:

* Medicine Name
* Dosage
* Reminder Time
* Frequency
* Additional Instructions

## 📸 Application Screenshots

Add screenshots of your application here:

```markdown
![Home Page](screenshots/home.png)

![Add Medicine](screenshots/add-medicine.png)

![Medicine List](screenshots/medicine-list.png)
```

## 🌐 Deployment

The application can be deployed using platforms such as **Render**.

For deployment, the project can use:

```text
Procfile
```

Example:

```text
web: gunicorn app:app
```

## 🔮 Future Enhancements

* 🔔 Browser notifications
* 📧 Email reminders
* 📱 SMS notifications
* 👤 User authentication
* 📊 Medication history
* 🗓️ Calendar-based medication scheduling
* ☁️ Cloud database integration
* 📱 Mobile application
* 🤖 AI-based medication assistance

## 🎯 Project Objective

The main objective of this project is to develop a simple and accessible digital solution that helps users **manage their medication schedules and avoid missing important medicine doses**.

## 👩‍💻 Author

**Dhanushya A**

B.Sc. Information Technology | Web Developer | Python Developer

### Skills Used

`Python` `Flask` `HTML` `CSS` `JavaScript` `SQLite`

## 📄 License

This project is created for educational and development purposes.
