import MasterPage from "@/components/MasterPage";

const Suppliers = () => {
  const fields = [
    { name: "code", label: "supplier_code", type: "text", required: true },
    { name: "name", label: "supplier_name", type: "text", required: true },
    { name: "contact_person", label: "contact_person", type: "text" },
    { name: "contact_email", label: "contact_email", type: "email" },
    { name: "contact_phone", label: "contact_phone", type: "tel" },
    { name: "address", label: "address", type: "text" },
    { name: "payment_terms", label: "payment_terms", type: "text" },
    { name: "rating", label: "rating", type: "number", step: "0.1", min: "0", max: "5" },
  ];

  const columns = [
    { key: "code", label: "supplier_code" },
    { key: "name", label: "supplier_name" },
    { key: "contact_person", label: "contact_person" },
    { key: "contact_email", label: "contact_email" },
    { key: "contact_phone", label: "contact_phone" },
    { key: "rating", label: "rating" },
    { key: "is_active", label: "status", isBadge: true },
  ];

  return (
    <MasterPage
      endpoint="suppliers"
      titleKey="suppliers_title"
      subtitleKey="suppliers_subtitle"
      addButtonKey="add_supplier"
      createTitleKey="create_new_supplier"
      fields={fields}
      columns={columns}
      searchFields={["name", "code"]}
    />
  );
};

export default Suppliers;
