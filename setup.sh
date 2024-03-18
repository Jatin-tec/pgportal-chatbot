#!/bin/bash
python db_setup.py FAQ Departments
python load_faq_data.py
python load_departments.py