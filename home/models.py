from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from autoslug import AutoSlugField
from django.utils.text import slugify
from django.db.models import Sum
# Create your models here.

class Blog(models.Model):

    title=models.CharField(max_length=100)
    description=models.CharField(max_length=300)
    user=models.ForeignKey(User,on_delete=models.RESTRICT)


# models.py


class CustomPermissions(models.Model):
    class Meta:
        permissions = [
            ('view_dashboard', 'Can view dashboard'),
            ("view_balance_sheet", "Can view balance sheet"),
            ("view_store", "Can view store"),
            ("view_reports", "Can view reports"),
            ("view_inventory", "Can view inventory"),
            # Add more custom permissions here
        ]

class Project(models.Model):
    name = models.CharField(max_length=100)
    is_deleted=models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Finish_Product_Category(models.Model):
    name = models.CharField(max_length=100)
    is_deleted=models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Final_Product(models.Model):
        ACTIVE = 'Atcive'
        INACTIVE = 'Inactive'

        STATUS_TYPE_CHOICES = [
        (ACTIVE , 'Active'),
        (INACTIVE ,'Inactive'),
    ]

        category=models.ForeignKey(Finish_Product_Category,on_delete=models.RESTRICT)
        productname=models.CharField(max_length=255,unique=True)
        product_size=models.CharField(max_length=255)
        # product_sale_price=models.CharField(max_length=255)
        product_quantity=models.CharField(max_length=255,null=True,blank=True )
        unit=models.CharField(max_length=255,default="Nos")
        weight=models.FloatField(max_length=255,default=0,null=True,blank=True)
        # product_status=models.CharField(max_length=50,choices=STATUS_TYPE_CHOICES)
        product_status=models.BooleanField(default=True)
        is_deleted = models.BooleanField(default=False)
        pro_img=models.ImageField(upload_to="uploaded/products/",null=True)
        product_slug=AutoSlugField(populate_from="productname",unique=True,null=True,default=None)
        def __str__(self):
            return f"{self.productname}"
        
        def get_price_for_customer(self, customer):
            # Get the price for this product for a specific customer
            try:
                return self.product_price.get(customer=customer).price
            except Product_Price.DoesNotExist:
                return None    
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    is_deleted=models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Unit(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):

    ACTIVE = 'Atcive'
    INACTIVE = 'Inactive'

    STATUS_TYPE_CHOICES = [
        (ACTIVE , 'Active'),
        (INACTIVE ,'Inactive'),
    ]

    category=models.ForeignKey(Category,on_delete=models.RESTRICT)
    category=models.ForeignKey(Category,on_delete=models.RESTRICT)
    productname=models.CharField(max_length=255,unique=True)
    product_size=models.CharField(max_length=255)
    # product_sale_price=models.CharField(max_length=255)
    product_quantity=models.CharField(max_length=255,null=True,blank=True )
    unit=models.CharField(max_length=255,default="Nos")
    weight=models.FloatField(max_length=255,default=0,null=True,blank=True)
    # product_status=models.CharField(max_length=50,choices=STATUS_TYPE_CHOICES)
    product_status=models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    pro_img=models.ImageField(upload_to="uploaded/products/",null=True,blank=True)
    # product_slug=AutoSlugField(populate_from=lambda instance: f"{instance.productname}-{instance.category}-{instance.id}",unique=True,null=True,default=None)
    product_slug=AutoSlugField(populate_from=None,unique=True,null=True,default=None)

    def __str__(self):
        return f"{self.productname}"
    
    def generate_slug(self):
        # Combine the fields and retain dots
        raw_slug = f"{self.productname}-{self.category}-{self.id or ''}".strip('-')
        # Replace spaces with hyphens and retain the dot (.) in the slug
        preprocessed_slug = raw_slug.replace(' ', '-')
        return ''.join(
            char if char.isalnum() or char in ['-', '.'] else '-' for char in preprocessed_slug.lower()
        )

    def save(self, *args, **kwargs):
        # Save to ensure ID is available for slug generation
        if not self.pk:
            super().save(*args, **kwargs)
        self.product_slug = self.generate_slug()
        super().save(*args, **kwargs)
    
    def get_price_for_customer(self, customer):
        # Get the price for this product for a specific customer
        try:
            return self.product_price.get(customer=customer).price
        except Product_Price.DoesNotExist:
            return None
        
    def get_current_stock(self):
        """Calculate the current stock of this product."""
        grn_total = Store_Purchase_Product.objects.filter(product_id=self.id).aggregate(total=Sum('quantity'))['total'] or 0
        issue_total = Store_Issue_Product.objects.filter(product_id=self.id).aggregate(total=Sum('quantity'))['total'] or 0
        sale_total = Sales_Receipt_Product.objects.filter(product_id=self.id).aggregate(total=Sum('quantity'))['total'] or 0
        current_stock = grn_total - issue_total - sale_total
        return current_stock
    
    def change_status(self):
        """Calculate the current stock of this product."""
        current_stock = self.get_current_stock()
        if current_stock <= 0:
            product=Product.objects.get(id=self.id)
            product.product_status=False
            product.save()
        else:
            product=Product.objects.get(id=self.id)
            product.product_status=True
            product.save()
        print(self.product_status)

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=0)  # Total quantity of the product in stock

    def __str__(self):
        return f"{self.product.productname} - {self.quantity} units"

    
# class GatePass(models.Model):
#     products = models.ManyToManyField(Product, through='GatePassProduct')
#     date_created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Gate Pass {self.id} - {self.date_created.strftime('%Y-%m-%d')}"
    

class GatePass(models.Model):
    products = models.ManyToManyField(Product, through='GatePassProduct')
    date_created = models.DateTimeField(auto_now_add=True)
    vehicle = models.CharField(max_length=255)
    driver_phone_number = models.CharField(max_length=20)
    dispatch_for = models.CharField(max_length=255)
    name_of_site = models.CharField(max_length=255)
    person_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    returnable=models.BooleanField(null=True)
    # prepared_by=models.CharField(max_length=255,default='')
    # authorized_by=models.CharField(max_length=255,default='')

    def __str__(self):
        return f"Gate Pass {self.id} - {self.date_created.strftime('%Y-%m-%d')}"
    
class GatePassProduct(models.Model):
    gatepass = models.ForeignKey(GatePass, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.IntegerField()
    remarks=models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return f"{self.product.productname} (Qty: {self.quantity})"
    
class Customer(models.Model):
    coname=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    adress=models.CharField(max_length=255)
    contact=models.CharField(max_length=12,null=True,unique=True,blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.coname
        # return f"{self.coname.capitalize()} "

class Sales_Receipt(models.Model):
    products = models.ManyToManyField(Product, through='Sales_Receipt_Product')
    date_created = models.DateTimeField(auto_now_add=True)
    customer_name =  models.ForeignKey(Customer,on_delete=models.RESTRICT,null=True)
    customer =  models.CharField(max_length=220,null=True,blank=True)
    phone_number = models.CharField(max_length=12)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT,null=True)
    make_transaction = models.BooleanField(default=False)
    is_cash = models.BooleanField(default=False)

    def __str__(self):
        return f"Sale Receipt {self.id} - {self.date_created.strftime('%Y-%m-%d')}"

class Sales_Receipt_Product(models.Model):
    salereceipt = models.ForeignKey(Sales_Receipt, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField()
    unit_price = models.FloatField()
    amount = models.FloatField()
    def __str__(self):
        return f"{self.product.productname} (Qty: {self.quantity})"
    
class Store_Issue_Note(models.Model):
    products = models.ManyToManyField(Product, through='Store_Issue_Product')
    date_created = models.DateTimeField(auto_now_add=True)
    project =  models.ForeignKey(Project,on_delete=models.PROTECT,null=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT,null=True)

    def __str__(self):
        return f"Store Issue {self.id} - {self.date_created.strftime('%Y-%m-%d')}"

class Store_Issue_Product(models.Model):
    store_issue_note = models.ForeignKey(Store_Issue_Note, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.productname} (Qty: {self.quantity})"
    
class Store_Purchase_Note(models.Model):
    products = models.ManyToManyField(Product, through='Store_Purchase_Product')
    date_created = models.DateTimeField(auto_now_add=True)
    project =  models.ForeignKey(Project,on_delete=models.PROTECT,null=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT,null=True)
    def __str__(self):
        return f"Store Purchase {self.id} - {self.date_created.strftime('%Y-%m-%d')}"

class Store_Purchase_Product(models.Model):
    store_purchase_note = models.ForeignKey(Store_Purchase_Note, on_delete=models.RESTRICT)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.product.productname} (Qty: {self.quantity})"
    
class Employee(models.Model):
    name=models.CharField(max_length=255)
    adress=models.CharField(max_length=255,null=True,blank=True)
    contact=models.CharField(max_length=12,null=True,unique=True,blank=True)
    job=models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name.capitalize()}"
    
class Suppliers(models.Model):
    coname=models.CharField(max_length=255)
    name=models.CharField(max_length=255)
    adress=models.CharField(max_length=255)
    contact=models.CharField(max_length=12,null=True,unique=True,blank=True)
    description=models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.coname
    
    
class Cheque(models.Model):
    customer=models.ForeignKey(Customer, on_delete=models.RESTRICT)
    cheque_number=models.CharField(max_length=20,null=True,blank=True)
    cheque_amount=models.CharField(max_length=20,null=True,blank=True)
    cheque_date=models.DateField()
    bank_name=models.CharField(max_length=50,null=True,blank=True)
    status=models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.customer} {self.cheque_number}"
        # return f"{self.customer} {self.cheque_number}".capitalize()

class Product_Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT, related_name='product_price')
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    price = models.FloatField()
    is_deleted=models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'customer')  # Ensure each customer has one price per product

class Account(models.Model):
    ASSET = 'Asset'
    LIABILITY = 'Liability'
    EQUITY = 'Equity'
    REVENUE = 'Revenue'
    EXPENSE = 'Expense'
    GAIN = 'Gain'
    LOSS = 'Loss'
    COMMITMENT = 'Commitment'
    COMMITMENT_RECEIVED = 'Commitment_Received'

    ACCOUNT_TYPE_CHOICES = [
        (ASSET, 'Asset'),
        (LIABILITY, 'Liability'),
        (EQUITY, 'Equity'),
        (REVENUE, 'Revenue'),
        (EXPENSE, 'Expense'),
        (GAIN, 'Gain'),
        (LOSS, 'Loss'),
        (COMMITMENT , 'Commitment'),
        (COMMITMENT_RECEIVED,'Commitment_Received')
    ]
    name=models.CharField(max_length=50,null=True ,blank=True)
    employee=models.OneToOneField(Employee, on_delete=models.RESTRICT ,null=True,blank=True)
    customer=models.OneToOneField(Customer, on_delete=models.RESTRICT ,null=True,blank=True)
    supplier=models.OneToOneField(Suppliers, on_delete=models.RESTRICT,null=True,blank=True)
    cheque=models.OneToOneField(Cheque, on_delete=models.RESTRICT,null=True,blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    date = models.DateTimeField(default=datetime.now())
    is_deleted=models.BooleanField(default=False)
    def __str__(self):
        if self.name:
            return f'{self.name}'
        elif self.customer:
            return f'{self.customer}'
        elif self.supplier:
            return f'{self.supplier}'
        elif self.cheque:
            return f'{self.cheque}'
    
class Transaction(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    debit_account = models.ForeignKey(Account, related_name='debit_transactions', on_delete=models.RESTRICT)
    credit_account = models.ForeignKey(Account, related_name='credit_transactions', on_delete=models.RESTRICT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.date} - {self.description}"