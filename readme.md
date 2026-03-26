# 🔋 BSMS – Battery Sales Management System

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/status-Active-success)
![Made With](https://img.shields.io/badge/Made%20With-Python-orange)
![UI](https://img.shields.io/badge/UI-Tkinter%20%7C%20ttkbootstrap-blueviolet)

---

An open-source desktop application built with Python to manage battery sales, inventory, and customer operations efficiently.

---

## 🧾 Project Background

This project was inspired by real-world challenges observed in a business that managed sales and inventory manually.

The goal was to design a **simple, practical, and user-friendly system** to digitize daily operations.

---

## 🚀 Features

### 📦 Inventory Management

* Add and manage battery products
* Track stock levels
* Support for multiple battery types

### 💰 Sales & Billing

* Record sales transactions
* Track payments and balances

### 👥 Customer Management

* Store customer details
* Track outstanding balances

### 🔐 User & Permissions

* Role-based access (Admin / Staff)

### ⚙️ Settings

* Database switching (Admin)
* Backup system
* Theme selection

---

## 🧠 Tech Stack

* Python
* Tkinter + ttkbootstrap
* SQLite
* ReportLab
* python-dotenv

---

## 📁 Project Structure

```bash
BSMS/
├── main.py
├── database.py
├── requirements.txt
├── README.md
├── .env.example
├── ui/
├── utils/
├── assets/
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/shreekanthkapparagaon/BSMS.git
cd BSMS
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure environment

```bash
copy .env.example .env   # Windows
```

Example `.env`:

```bash
APP_MODE=DEV
DEFAULT_DB_NAME=bsms.db
DEFAULT_THEME=superhero
ALLOW_DB_SWITCH=True
```

---

## ▶️ Run the Application

```bash
python main.py
```

---

## 🔑 Default Login

```bash
Username: admin
Password: admin123
```

---

## ⚙️ Application Modes

The application supports two modes controlled via `.env`:

### 🧪 DEV Mode

```env
APP_MODE=DEV
```

* Auto login enabled
* Faster testing
* Useful during development

---

### 🚀 PROD Mode

```env
APP_MODE=PROD
```

* Login required
* Full security enabled
* Recommended for real usage

---

## 🗄️ Database

* SQLite database is created automatically
* Default location:

  ```
  APPDATA/BSMS/bsms.db
  ```
* Can be changed from Settings (Admin only)

---

## 💾 Backup

* Manual database backup available
* Save `.db` file anywhere

---

## 📦 Executable

A pre-built Windows executable is available in the [Releases](https://github.com/shreekanthkapparagaon/BSMS/releases) section.

- No Python setup required  
- Ready to use  

Developers can also run the application directly from source.

---

## 🤝 Contributing

```bash
# Fork → Clone → Create branch → Commit → Push
git checkout -b feature-name
git commit -m "Add feature"
git push origin feature-name
```

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Shreekant N.K**

---

## ⭐ Support

If you find this project useful:

* ⭐ Star the repository
* 🍴 Fork it
* 🛠 Contribute

---
