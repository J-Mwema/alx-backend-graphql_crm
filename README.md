# ALX Backend GraphQL CRM

A Django-based CRM system with advanced GraphQL API for customer, product, and order management. Supports complex mutations, bulk operations, and robust filtering.

## Features
- Create, bulk-create, and manage customers, products, and orders via GraphQL
- Advanced filtering and search using django-filter
- Custom error handling and validation

## Project Structure
- `alx_backend_graphql/` — Django project (settings, schema)
- `crm/` — Main app (models, schema, filters, migrations)
- `graphql_crm/` — (if present) for legacy or extended schemas

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply migrations:
   ```bash
   python manage.py makemigrations crm
   python manage.py migrate
   ```
3. Run the server:
   ```bash
   python manage.py runserver
   ```
4. Access GraphQL at: [http://localhost:8000/graphql](http://localhost:8000/graphql)

## GraphQL Usage
### Example Mutations
```graphql
# Create a single customer
mutation {
  createCustomer(name: "Alice", email: "alice@example.com", phone: "+1234567890") {
    customer { id name email phone }
    message
  }
}

# Bulk create customers
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers { id name email }
    errors
  }
}

# Create a product
mutation {
  createProduct(input: { name: "Laptop", price: 999.99, stock: 10 }) {
    product { id name price stock }
  }
}

# Create an order with products
mutation {
  createOrder(input: { customerId: "1", productIds: ["1", "2"] }) {
    order {
      id
      customer { name }
      products { name price }
      totalAmount
      orderDate
    }
  }
}
```

### Example Filtering Queries
```graphql
# Filter customers by name and creation date
query {
  allCustomers(name_Icontains: "Ali") {
    edges { node { id name email } }
  }
}

# Filter products by price range and sort by stock
query {
  allProducts(price_Gte: 100, price_Lte: 1000, orderBy: "-stock") {
    edges { node { id name price stock } }
  }
}
```

## Testing
- Use the GraphiQL interface at `/graphql` to run queries and mutations interactively.

## License
MIT
