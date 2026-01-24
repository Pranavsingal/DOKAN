# 🛍️ Dokan – Your Digital Dukaan

**Dokan** is a lightweight, full-featured digital retail solution designed specifically for Indian *kirana* (grocery) stores. Developed during the **Global Innovation Hackathon**, Dokan equips small shop owners with an all-in-one platform for **inventory**, **billing**, and **customer management**.

---

## ⚡ The Problem

Indian small retailers face daily challenges that limit growth and efficiency:

* ❌ **Manual inventory** causes 20–25% stock-related losses
* 🕒 Over **50% of time** is spent on billing & bookkeeping
* 📉 **Poor customer engagement** affects retention and revenue

---

## ✅ Our Solution

Dokan offers a modern, intuitive platform that simplifies operations:

* 📦 **Real-time stock tracking** with alerts
* 🧾 **GST-compliant invoices** generated in seconds
* 📊 **Smart analytics** with sales trends and performance reports
* 🌐 **Cross-device access** — works on mobile, tablet, and desktop
* 🛠️ **No special hardware needed**

---

## ✨ Key Features

### 📦 Inventory Management

* Automatic low-stock alerts
* Real-time stock updates
* Downloadable inventory reports

### 🧾 Billing & Accounting

* Quick GST billing
* Printable and downloadable invoices
* Error-free calculations

### 👥 Customer Management

* Loyalty program integration
* SMS marketing for retention
* Customer profiles and history

### 📊 Analytics Dashboard

* Sales trends and growth insights
* Bestseller tracking
* Performance snapshots for informed decisions

---

## 📸 Demo Highlights

* 🧭 Guided flow with intuitive navigation
* 🔄 Real-time inventory & billing sync
* ⚡ Instant billing — zero manual errors

> “Dokan changed how I manage my store. It's easy and saves time!”
> “Sales have grown, and customers keep coming back more often.”

---

## 📈 Real Impact

* 🔻 **30% reduction** in stockouts
* 🔼 **15% revenue increase**
* ⏱️ **50% reduction** in billing time
  
---

## 👨‍💻 My Role & Contributions

- Designed and implemented the Flask backend architecture
- Developed inventory and billing logic with real-time updates
- Integrated AI modules for analytics and prediction
- Handled CSV-based data management using Pandas
- Built and connected frontend templates with backend APIs

---

## 🚀 Tech Stack

| Layer         | Technology                                  |
| ------------- | ------------------------------------------- |
| **Frontend**  | HTML, CSS, JavaScript (via Flask templates) |
| **Backend**   | Python, Flask                               |
| **Database**  | CSV files handled with Pandas               |
| **AI Module** | Python, Pandas, scikit-learn                |

---

## 🧠 System Architecture

Dokan follows a modular backend-first architecture designed for simplicity and scalability:

- **Flask Backend** handles routing, authentication, business logic, and API responses
- **CSV + Pandas Layer** is used for lightweight data storage and fast prototyping during hackathon development
- **AI Module** processes sales and customer data to generate insights and predictions
- **Template-based Frontend** renders dynamic data using Flask and JavaScript

This separation of concerns allows easy migration to a relational database (MySQL/PostgreSQL) and REST-based frontend in future iterations.

---

## 🤖 AI & Data Intelligence

Dokan integrates machine learning to enhance decision-making for store owners:

- **Sales Trend Analysis** using historical billing data
- **Demand Prediction** for frequently sold products
- **Customer Sentiment Insights** based on feedback data
- **Data Preprocessing & Feature Engineering** using Pandas
- **Modeling** using scikit-learn for lightweight prediction tasks

The AI pipeline was designed to be efficient, interpretable, and suitable for small retail datasets.

---

## 📂 Data Storage Design Choice

CSV-based storage was intentionally used during hackathon development to:

- Enable fast iteration without database setup overhead
- Ensure portability and ease of deployment
- Allow quick data analysis using Pandas

The system architecture supports seamless migration to MySQL or PostgreSQL for production-scale deployment.

---

## 🧪 How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Pranavsingal/GIH.git
cd GIH

# 2. Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 🎯 Vision & Mission

**Vision**
Empower India’s 13M+ small retailers with accessible digital tools.

**Mission**
Build a simple, scalable platform to modernize Indian retail — one *dukaan* at a time.

---
## 📜 License

This project is licensed under the **MIT License** — open to use and modify freely.
