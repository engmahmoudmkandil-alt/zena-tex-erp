import MasterPage from "@/components/MasterPage";

const Employees = () => {
  const fields = [
    { name: "code", label: "employee_code", type: "text", required: true },
    { name: "name", label: "employee_name", type: "text", required: true },
    { name: "email", label: "email", type: "email" },
    { name: "phone", label: "phone", type: "tel" },
    { name: "department", label: "department", type: "text" },
    { name: "position", label: "position", type: "text" },
    { name: "hire_date", label: "hire_date", type: "date" },
    { name: "salary", label: "salary", type: "number", step: "0.01" },
  ];

  const columns = [
    { key: "code", label: "employee_code" },
    { key: "name", label: "employee_name" },
    { key: "department", label: "department" },
    { key: "position", label: "position" },
    { key: "hire_date", label: "hire_date", isDate: true },
    { key: "is_active", label: "status", isBadge: true },
  ];

  return (
    <MasterPage
      endpoint="employees"
      titleKey="employees_title"
      subtitleKey="employees_subtitle"
      addButtonKey="add_employee"
      createTitleKey="create_new_employee"
      fields={fields}
      columns={columns}
      searchFields={["name", "code"]}
    />
  );
};

export default Employees;
