import MasterPage from "@/components/MasterPage";

const Customers = () => {
  const fields = [
    { name: "code", label: "customer_code", type: "text", required: true },
    { name: "name", label: "customer_name", type: "text", required: true },
    { name: "contact_person", label: "contact_person", type: "text" },
    { name: "contact_email", label: "contact_email", type: "email" },
    { name: "contact_phone", label: "contact_phone", type: "tel" },
    { name: "address", label: "address", type: "text" },
    { name: "payment_terms", label: "payment_terms", type: "text" },
    { name: "credit_limit", label: "credit_limit", type: "number", step: "0.01" },
  ];

  const columns = [
    { key: "code", label: "customer_code" },
    { key: "name", label: "customer_name" },
    { key: "contact_person", label: "contact_person" },
    { key: "contact_email", label: "contact_email" },
    { key: "credit_limit", label: "credit_limit", isNumber: true },
    { key: "outstanding_balance", label: "outstanding_balance", isNumber: true },
    { key: "is_active", label: "status", isBadge: true },
  ];

  return (
    <MasterPage
      endpoint="customers"
      titleKey="customers_title"
      subtitleKey="customers_subtitle"
      addButtonKey="add_customer"
      createTitleKey="create_new_customer"
      fields={fields}
      columns={columns}
      searchFields={["name", "code"]}
    />
  );
};

export default Customers;
