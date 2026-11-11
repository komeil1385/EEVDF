
# 🔄 Process Synchronization: A Comparative Study

This directory contains a comprehensive academic and educational comparative study on concurrency and process synchronization, focusing on six fundamental topics:
1. **Peterson's Algorithm**
2. **Dekker's Algorithm**
3. **Semaphore**
4. **Monitor**
5. **Readers–Writers Problem**
6. **Dining Philosophers Problem**

---

## 📑 Technical Documentation & Reports (Persian & English)

The comprehensive technical reports (including detailed comparison tables, flowcharts, code listings, and university-level exercises with solutions) are available in both English and Persian:

* 🇬🇧 **English Version (`Process_Synchronization_Comparison_EN.docx`):**  
  [![Preview EN](https://img.shields.io/badge/Live_Preview-English_Report-blue?style=flat-square)](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fkomeil1385%2FEEVDF%2Fmain%2FProcess-Synchronization-Mechanisms%2FProcess_Synchronization_Comparison_EN.docx)
  [![Download EN](https://img.shields.io/badge/Download-.docx-success?style=flat-square)](./Process_Synchronization_Comparison_EN.docx)

* 🇮🇷 **Persian Version (`Process_Synchronization_Comparison_FA.docx`):**  
  [![Preview FA](https://img.shields.io/badge/پیش‌نمایش_آنلاین-گزارش_فارسی-blue?style=flat-square)](https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fraw.githubusercontent.com%2Fkomeil1385%2FEEVDF%2Fmain%2FProcess-Synchronization-Mechanisms%2FProcess_Synchronization_Comparison_FA.docx)
  [![Download FA](https://img.shields.io/badge/دانلود_فایل-.docx-success?style=flat-square)](./Process_Synchronization_Comparison_FA.docx)

---

## 📊 Summary of Evaluated Criteria
The study features a master comparison table evaluating all topics against 13 key properties:
* Number of Processes & Flag Arrays / Turn Variables
* Busy Waiting & Temporary Back-off
* Mutual Exclusion, Progress, and Bounded Waiting
* Deadlock Freedom & Starvation Freedom
* Complexity, Fairness, Preemption, and Scalability

---

## 🚀 How to Run Code Examples
All C/POSIX-threads source code files and compilation instructions are detailed inside the reports. To compile and test a specific algorithm:
```bash
gcc -std=c11 -O2 -pthread -o peterson peterson.c
./peterson
