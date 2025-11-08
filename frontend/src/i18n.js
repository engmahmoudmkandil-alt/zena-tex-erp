import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      // Common
      "app_name": "InventoryPro",
      "loading": "Loading...",
      "search": "Search",
      "add": "Add",
      "edit": "Edit",
      "delete": "Delete",
      "save": "Save",
      "cancel": "Cancel",
      "create": "Create",
      "update": "Update",
      "actions": "Actions",
      "submit": "Submit",
      "close": "Close",
      "confirm": "Confirm",
      "yes": "Yes",
      "no": "No",
      "back": "Back",
      "next": "Next",
      "refresh": "Refresh",
      
      // Navigation
      "nav_dashboard": "Dashboard",
      "nav_products": "Products",
      "nav_warehouses": "Warehouses",
      "nav_inventory": "Inventory",
      "nav_stock_moves": "Stock Moves",
      "nav_adjustments": "Adjustments",
      "nav_user_management": "User Management",
      "nav_audit_logs": "Audit Logs",
      "nav_boms": "BOMs",
      "nav_work_centers": "Work Centers",
      "nav_employees": "Employees",
      "nav_suppliers": "Suppliers",
      "nav_customers": "Customers",
      "nav_logout": "Logout",
      
      // Auth
      "sign_in": "Sign In",
      "sign_up": "Sign Up",
      "email": "Email",
      "password": "Password",
      "confirm_password": "Confirm Password",
      "full_name": "Full Name",
      "phone": "Phone",
      "sign_in_with_google": "Sign in with Google",
      "dont_have_account": "Don't have an account?",
      "already_have_account": "Already have an account?",
      "sign_in_to_account": "Sign in to your account",
      "create_account": "Create Account",
      
      // Dashboard
      "dashboard_title": "Dashboard",
      "dashboard_subtitle": "Overview of your inventory system",
      "total_products": "Total Products",
      "warehouses": "Warehouses",
      "total_stock_units": "Total Stock Units",
      "low_stock_items": "Low Stock Items",
      "recent_stock_moves": "Recent Stock Moves",
      
      // Products
      "products_title": "Products",
      "products_subtitle": "Manage your product catalog",
      "add_product": "Add Product",
      "create_new_product": "Create New Product",
      "product_code": "Product Code",
      "product_name": "Product Name",
      "description": "Description",
      "unit": "Unit",
      "unit_of_measure": "Unit of Measure",
      "created": "Created",
      "search_products": "Search products by name or code...",
      
      // Warehouses
      "warehouses_title": "Warehouses & Bins",
      "warehouses_subtitle": "Manage storage locations",
      "add_warehouse": "Add Warehouse",
      "add_bin": "Add Bin",
      "warehouse_code": "Warehouse Code",
      "warehouse_name": "Warehouse Name",
      "location": "Location",
      "bins": "Bins",
      "create_new_warehouse": "Create New Warehouse",
      "create_new_bin": "Create New Bin",
      "bin_code": "Bin Code",
      "bin_name": "Bin Name",
      "select_warehouse": "Select Warehouse",
      
      // Inventory
      "inventory_title": "Inventory",
      "inventory_subtitle": "Current stock levels across all locations",
      "filter_by_product": "Filter by Product",
      "filter_by_warehouse": "Filter by Warehouse",
      "all_products": "All Products",
      "all_warehouses": "All Warehouses",
      "quantity": "Quantity",
      "last_updated": "Last Updated",
      
      // BOMs
      "boms_title": "Bills of Materials",
      "boms_subtitle": "Manage product BOMs and recipes",
      "add_bom": "Add BOM",
      "create_new_bom": "Create New BOM",
      "bom_name": "BOM Name",
      "finished_product": "Finished Product",
      "select_product": "Select Product",
      "components": "Components",
      "add_component": "Add Component",
      "component": "Component",
      "quantity_required": "Quantity Required",
      "version": "Version",
      "is_active": "Is Active",
      
      // Work Centers
      "work_centers_title": "Work Centers",
      "work_centers_subtitle": "Manage production work centers",
      "add_work_center": "Add Work Center",
      "create_new_work_center": "Create New Work Center",
      "work_center_code": "Work Center Code",
      "work_center_name": "Work Center Name",
      "capacity": "Capacity",
      "efficiency": "Efficiency",
      "cost_per_hour": "Cost per Hour",
      
      // Employees
      "employees_title": "Employees",
      "employees_subtitle": "Manage employee records",
      "add_employee": "Add Employee",
      "create_new_employee": "Create New Employee",
      "employee_code": "Employee Code",
      "employee_name": "Employee Name",
      "department": "Department",
      "position": "Position",
      "hire_date": "Hire Date",
      "salary": "Salary",
      "status": "Status",
      "active": "Active",
      "inactive": "Inactive",
      
      // Suppliers
      "suppliers_title": "Suppliers",
      "suppliers_subtitle": "Manage supplier information",
      "add_supplier": "Add Supplier",
      "create_new_supplier": "Create New Supplier",
      "supplier_code": "Supplier Code",
      "supplier_name": "Supplier Name",
      "contact_person": "Contact Person",
      "contact_email": "Contact Email",
      "contact_phone": "Contact Phone",
      "address": "Address",
      "payment_terms": "Payment Terms",
      "rating": "Rating",
      
      // Customers
      "customers_title": "Customers",
      "customers_subtitle": "Manage customer information",
      "add_customer": "Add Customer",
      "create_new_customer": "Create New Customer",
      "customer_code": "Customer Code",
      "customer_name": "Customer Name",
      "credit_limit": "Credit Limit",
      "outstanding_balance": "Outstanding Balance",
      
      // Messages
      "success_created": "Created successfully",
      "success_updated": "Updated successfully",
      "success_deleted": "Deleted successfully",
      "error_create": "Failed to create",
      "error_update": "Failed to update",
      "error_delete": "Failed to delete",
      "error_load": "Failed to load data",
      "no_data_found": "No data found",
      "confirm_delete": "Are you sure you want to delete this item?"
    }
  },
  ar: {
    translation: {
      // Common
      "app_name": "إنفينتوري برو",
      "loading": "جاري التحميل...",
      "search": "بحث",
      "add": "إضافة",
      "edit": "تعديل",
      "delete": "حذف",
      "save": "حفظ",
      "cancel": "إلغاء",
      "create": "إنشاء",
      "update": "تحديث",
      "actions": "الإجراءات",
      "submit": "إرسال",
      "close": "إغلاق",
      "confirm": "تأكيد",
      "yes": "نعم",
      "no": "لا",
      "back": "رجوع",
      "next": "التالي",
      "refresh": "تحديث",
      
      // Navigation
      "nav_dashboard": "لوحة التحكم",
      "nav_products": "المنتجات",
      "nav_warehouses": "المستودعات",
      "nav_inventory": "المخزون",
      "nav_stock_moves": "حركات المخزون",
      "nav_adjustments": "التسويات",
      "nav_user_management": "إدارة المستخدمين",
      "nav_audit_logs": "سجلات التدقيق",
      "nav_boms": "قوائم المواد",
      "nav_work_centers": "مراكز العمل",
      "nav_employees": "الموظفون",
      "nav_suppliers": "الموردون",
      "nav_customers": "العملاء",
      "nav_logout": "تسجيل الخروج",
      
      // Auth
      "sign_in": "تسجيل الدخول",
      "sign_up": "إنشاء حساب",
      "email": "البريد الإلكتروني",
      "password": "كلمة المرور",
      "confirm_password": "تأكيد كلمة المرور",
      "full_name": "الاسم الكامل",
      "phone": "الهاتف",
      "sign_in_with_google": "تسجيل الدخول باستخدام جوجل",
      "dont_have_account": "ليس لديك حساب؟",
      "already_have_account": "هل لديك حساب بالفعل؟",
      "sign_in_to_account": "تسجيل الدخول إلى حسابك",
      "create_account": "إنشاء حساب",
      
      // Dashboard
      "dashboard_title": "لوحة التحكم",
      "dashboard_subtitle": "نظرة عامة على نظام المخزون الخاص بك",
      "total_products": "إجمالي المنتجات",
      "warehouses": "المستودعات",
      "total_stock_units": "إجمالي وحدات المخزون",
      "low_stock_items": "المنتجات منخفضة المخزون",
      "recent_stock_moves": "حركات المخزون الأخيرة",
      
      // Products
      "products_title": "المنتجات",
      "products_subtitle": "إدارة كتالوج المنتجات الخاص بك",
      "add_product": "إضافة منتج",
      "create_new_product": "إنشاء منتج جديد",
      "product_code": "كود المنتج",
      "product_name": "اسم المنتج",
      "description": "الوصف",
      "unit": "الوحدة",
      "unit_of_measure": "وحدة القياس",
      "created": "تاريخ الإنشاء",
      "search_products": "البحث عن المنتجات بالاسم أو الكود...",
      
      // Warehouses
      "warehouses_title": "المستودعات والأرفف",
      "warehouses_subtitle": "إدارة مواقع التخزين",
      "add_warehouse": "إضافة مستودع",
      "add_bin": "إضافة رف",
      "warehouse_code": "كود المستودع",
      "warehouse_name": "اسم المستودع",
      "location": "الموقع",
      "bins": "الأرفف",
      "create_new_warehouse": "إنشاء مستودع جديد",
      "create_new_bin": "إنشاء رف جديد",
      "bin_code": "كود الرف",
      "bin_name": "اسم الرف",
      "select_warehouse": "اختر المستودع",
      
      // Inventory
      "inventory_title": "المخزون",
      "inventory_subtitle": "مستويات المخزون الحالية عبر جميع المواقع",
      "filter_by_product": "تصفية حسب المنتج",
      "filter_by_warehouse": "تصفية حسب المستودع",
      "all_products": "جميع المنتجات",
      "all_warehouses": "جميع المستودعات",
      "quantity": "الكمية",
      "last_updated": "آخر تحديث",
      
      // BOMs
      "boms_title": "قوائم المواد",
      "boms_subtitle": "إدارة قوائم المواد ووصفات المنتجات",
      "add_bom": "إضافة قائمة مواد",
      "create_new_bom": "إنشاء قائمة مواد جديدة",
      "bom_name": "اسم قائمة المواد",
      "finished_product": "المنتج النهائي",
      "select_product": "اختر المنتج",
      "components": "المكونات",
      "add_component": "إضافة مكون",
      "component": "المكون",
      "quantity_required": "الكمية المطلوبة",
      "version": "الإصدار",
      "is_active": "نشط",
      
      // Work Centers
      "work_centers_title": "مراكز العمل",
      "work_centers_subtitle": "إدارة مراكز العمل الإنتاجية",
      "add_work_center": "إضافة مركز عمل",
      "create_new_work_center": "إنشاء مركز عمل جديد",
      "work_center_code": "كود مركز العمل",
      "work_center_name": "اسم مركز العمل",
      "capacity": "السعة",
      "efficiency": "الكفاءة",
      "cost_per_hour": "التكلفة في الساعة",
      
      // Employees
      "employees_title": "الموظفون",
      "employees_subtitle": "إدارة سجلات الموظفين",
      "add_employee": "إضافة موظف",
      "create_new_employee": "إنشاء موظف جديد",
      "employee_code": "كود الموظف",
      "employee_name": "اسم الموظف",
      "department": "القسم",
      "position": "المنصب",
      "hire_date": "تاريخ التعيين",
      "salary": "الراتب",
      "status": "الحالة",
      "active": "نشط",
      "inactive": "غير نشط",
      
      // Suppliers
      "suppliers_title": "الموردون",
      "suppliers_subtitle": "إدارة معلومات الموردين",
      "add_supplier": "إضافة مورد",
      "create_new_supplier": "إنشاء مورد جديد",
      "supplier_code": "كود المورد",
      "supplier_name": "اسم المورد",
      "contact_person": "الشخص المسؤول",
      "contact_email": "البريد الإلكتروني",
      "contact_phone": "رقم الهاتف",
      "address": "العنوان",
      "payment_terms": "شروط الدفع",
      "rating": "التقييم",
      
      // Customers
      "customers_title": "العملاء",
      "customers_subtitle": "إدارة معلومات العملاء",
      "add_customer": "إضافة عميل",
      "create_new_customer": "إنشاء عميل جديد",
      "customer_code": "كود العميل",
      "customer_name": "اسم العميل",
      "credit_limit": "حد الائتمان",
      "outstanding_balance": "الرصيد المستحق",
      
      // Messages
      "success_created": "تم الإنشاء بنجاح",
      "success_updated": "تم التحديث بنجاح",
      "success_deleted": "تم الحذف بنجاح",
      "error_create": "فشل الإنشاء",
      "error_update": "فشل التحديث",
      "error_delete": "فشل الحذف",
      "error_load": "فشل تحميل البيانات",
      "no_data_found": "لم يتم العثور على بيانات",
      "confirm_delete": "هل أنت متأكد من حذف هذا العنصر؟"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
