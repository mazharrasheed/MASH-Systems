# Create your views here.

from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required,permission_required
from ..forms import  Sales_Receipt_ProductForm,Sales_ReceiptForm,Sales_Cash_Receipt_ProductForm,Sales_Cash_ReceiptForm
from ..models import Sales_Receipt, Sales_Receipt_Product,Product,Product_Price,Transaction,Account,Customer
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Avg,Min,Max,Count,Sum
from collections import defaultdict
from django.db import IntegrityError

@login_required
@permission_required('home.view_sales_receipt', login_url='/login/')
def list_sales(request):
    salereceipt_items_pro = {}
    total_amount = {}
    salereceipts = []
    customer = request.GET.get('customer')
    cash = request.GET.get('cash')

    # Filter based on customer or cash
    if customer:
        print("custemer")
        salereceipts = Sales_Receipt.objects.filter(is_cash=False)
    elif cash == "True":
        salereceipts = Sales_Receipt.objects.filter(is_cash=True)
    else:
        salereceipts = Sales_Receipt.objects.all()
        
    for x in salereceipts:
        # Count the number of products for each sale receipt
        salereceipt_items_pro[x.id] = Sales_Receipt_Product.objects.filter(salereceipt=x).count()
        # Get products for the sale receipt and aggregate the amount
        salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=x)
        total_amount[x.id] = salereceipt_products.aggregate(Sum('amount'))

    total_sale = sum(item['amount__sum'] or 0 for item in total_amount.values())

    # Prepare JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
        'total_sale': total_sale,
      })

    # Return HTML response for standard requests
    return render(request, 'sale/list_sales.html', {
        'salereceipts': salereceipts,
        'salereceipt_items_pro': salereceipt_items_pro,
        'total_amount': total_amount,
        'total_sale': total_sale,
        'customer': customer,
        'cash': cash,
    })

@login_required
@permission_required('home.add_sales_receipt', login_url='/login/')
def salereceipt(request):
    form = Sales_Receipt_ProductForm()
    form_salereceipt=Sales_ReceiptForm()
    return render(request, 'gatepass/create_gatepass.html', {
        'form': form,
        'form_salereceipt':form_salereceipt,   
    })

@login_required
@permission_required('home.add_sales_receipt', login_url='/login/')
def create_salereceipt(request, salereceipt_id=None):
    if salereceipt_id:
        salereceipt = get_object_or_404(Sales_Receipt, id=salereceipt_id)
    else:
        salereceipt = Sales_Receipt.objects.create()
        return redirect('create_salereceipt', salereceipt_id=salereceipt.id)
    if request.method == 'POST':
        form = Sales_Receipt_ProductForm(request.POST, salereceipt=salereceipt)
        form_salereceipt = Sales_ReceiptForm(request.POST, instance=salereceipt)
        if form.is_valid() and form_salereceipt.is_valid():
            salercpt=form_salereceipt.save(commit=False)
            salercpt.created_by=request.user
            salercpt.save()
            customer=form_salereceipt.cleaned_data.get('customer_name')
            product=form.cleaned_data.get('product')
            unit_price1=Product_Price.objects.get(is_deleted=False,customer=customer,product=product)
            unit_price = unit_price1.price
            qty = form.cleaned_data.get('quantity')
            amount=unit_price*qty
            salereceipt_product = form.save(commit=False)
            salereceipt_product.salereceipt = salereceipt
            salereceipt_product.unit_price = unit_price1.price
            salereceipt_product.amount = amount
            salereceipt_product.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
                rendered_products = render_to_string('sale/salereceipt_product_list.html', {
                    'salereceipt_products': salereceipt_products,
                    'salereceipt_id': salereceipt.id,
                })
                return JsonResponse({
                    'success': True,
                    'rendered_products': rendered_products,
                    'salereceipt_id': salereceipt.id,
                })
            return redirect('create_salereceipt', salereceipt_id=salereceipt.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                })
    else:
        form = Sales_Receipt_ProductForm(salereceipt=salereceipt)
        form_salereceipt = Sales_ReceiptForm(instance=salereceipt)

    salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
    return render(request, 'sale/create_salereceipt.html', {
        'form': form,
        'salereceipt_products': salereceipt_products,
        'form_salereceipt': form_salereceipt,
        'salereceipt': salereceipt,
    })

@login_required
@permission_required('home.change_sales_receipt', login_url='/login/')
def edit_salereceipt(request, salereceipt_id=None):
    update=True
    if salereceipt_id:
        salereceipt = get_object_or_404(Sales_Receipt, id=salereceipt_id)

    if request.method == 'POST':
        form = Sales_Receipt_ProductForm(request.POST, salereceipt=salereceipt)
        form_salereceipt = Sales_ReceiptForm(request.POST, instance=salereceipt)
        if form.is_valid() and form_salereceipt.is_valid():
            salercpt=form_salereceipt.save(commit=False)
            salercpt.created_by=request.user
            salercpt.save()
            salereceipt_product = form.save(commit=False)
            salereceipt_product.salereceipt = salereceipt
            salereceipt_product.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
                rendered_products = render_to_string('salereceipt/salereceipt_product_list.html', {
                    'salereceipt_products': salereceipt_products,
                    'salereceipt_id': salereceipt.id,
                })
                return JsonResponse({
                    'success': True,
                    'rendered_products': rendered_products,
                    'salereceipt_id': salereceipt.id,
                })
            return redirect('edit_salereceipt', salereceipt_id=salereceipt.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                })
    else:
        form = Sales_Receipt_ProductForm(salereceipt=salereceipt)
        form_salereceipt = Sales_ReceiptForm(instance=salereceipt)

    salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
    return render(request, 'sale/edit_salereceipt.html', {
        'form': form,
        'salereceipt_products': salereceipt_products,
        'form_salereceipt': form_salereceipt,
        'salereceipt': salereceipt,
        'update':update
    })

@login_required
@permission_required('home.delete_sales_receipt', login_url='/login/')
def delete_salereceipt_item(request,id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        product = get_object_or_404(Sales_Receipt_Product, id=id)
        salereceipt_id = request.POST.get('salereceipt_id')
        product.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
@permission_required('home.add_sales_receipt', login_url='/login/')
def create_cash_salereceipt(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if 'finalize' in request.POST:  # Finalize the purchase note
            form_salereceipt = Sales_Cash_ReceiptForm(request.POST)
            products = request.POST.getlist('products[]')
            if form_salereceipt.is_valid() and products:
                salercpt = form_salereceipt.save(commit=False)
                salercpt.created_by = request.user
                salercpt.is_cash = True
                salercpt.save()
                for product_data in products:
                    product_id, quantity , unit_price, amount= product_data.split(':')
                    Sales_Receipt_Product.objects.create(
                        salereceipt=salercpt,
                        product_id=product_id,
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=amount
                    )
                    Product.objects.get(id=product_id).change_status()
                return JsonResponse({'success': True, 'redirect_url': '/list-sales?cash=True'})
            else:
                return JsonResponse({'success': False, 'errors': 'Invalid form data or no products selected.'})
    else:
        form = Sales_Cash_Receipt_ProductForm()
        form_salereceipt = Sales_Cash_ReceiptForm()
    return render(request, 'sale/create_cash_salereceipt.html', {
        'form': form,
        'form_salereceipt': form_salereceipt,
    })

@login_required
@permission_required('home.change_sales_receipt', login_url='/login/')
def edit_cash_salereceipt(request,id):
    salercpt = get_object_or_404(Sales_Receipt, id=id)
    products = Sales_Receipt_Product.objects.filter(salereceipt=salercpt.id)
    if request.method == 'POST':
        form = Sales_Cash_ReceiptForm(request.POST, instance=salercpt)
        if form.is_valid():
            grn = form.save()
            product_data = request.POST.getlist('products[]')
            deleted_products = request.POST.getlist('deleted_products[]')
            # Delete removed products
            Sales_Receipt_Product.objects.filter(salereceipt=salercpt, product__id__in=deleted_products).delete()
            product_quantities = defaultdict(int)
            for product_info in product_data:
                try:
                    product_id, quantity,unit_price,amount = product_info.split(':')
                    product_quantities[product_id] += int(quantity)
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Invalid product data.'})

            for product_id, total_quantity in product_quantities.items():
                try:
                    product_instance = Product.objects.get(id=product_id)
                    product, created = Sales_Receipt_Product.objects.update_or_create(
                        salereceipt=salercpt, 
                        product=product_instance, 
                        defaults={
                            'quantity': total_quantity,
                            'unit_price': float(unit_price),
                            'amount': float(amount),
                        }
                    )

                    Product.objects.get(id=product_id).change_status()

                except Product.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f'Product with ID {product_id} does not exist.'})

            return JsonResponse({'success': True, 'redirect_url': '/list-sales?cash=True'})

        return JsonResponse({'success': False, 'message': 'Invalid form submission.'})

    context = {
        'salereceipt': salercpt,
        'products': products,
        'form_salereceipt': Sales_Cash_ReceiptForm(instance=salercpt),
        'form': Sales_Cash_Receipt_ProductForm(),
    }
    return render(request, 'sale/edit_cash_salereceipt.html', context)


@login_required
@permission_required('home.add_sales_receipt', login_url='/login/')
def cancel_salereceipt(request,id):
    # salereceipt_id=(request.GET.get('salereceipt_id'))
    salereceipt=get_object_or_404(Sales_Receipt,id=id)
    salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
    # 
    if salereceipt_products:
        for item in salereceipt_products:
            item.delete()
    salereceipt.delete()
    messages.success(request, "Your sale receipt canceled !") 
    return redirect('list_sales')

@login_required
@permission_required('home.delete_sales_receipt', login_url='/login/')
def delete_salereceipt(request, id):
    product_list=[]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'POST':
        salereceipt = get_object_or_404(Sales_Receipt, id=id)
        salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
        if salereceipt_products:
            for pro in salereceipt_products:
                product_list.append(pro.product)
            salereceipt_products.delete()  # Bulk delete all related products
            for i in product_list:
                i.change_status()
        salereceipt.delete()
        return JsonResponse({'success': True, 'message': 'Sale receipt deleted successfully!'})
    # For non-AJAX requests, handle as usual
    salereceipt = get_object_or_404(Sales_Receipt, id=id)
    salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
    if salereceipt_products:
        for pro in salereceipt_products:
            product_list.append(pro.product)
        salereceipt_products.delete()  # Bulk delete all related products
        # change stust of product after deletion of sale receipt
        for i in product_list:
            i.change_status()
        salereceipt_products.delete()  # Bulk delete all related products
    salereceipt.delete()
    messages.success(request, "Sale receipt deleted successfully!")
    return redirect('list_salereceipts')

@login_required
@permission_required('home.view_sales_receipt', login_url='/login/')
def print_salereceipt(request, salereceipt_id):
    # Fetch the salereceipt instance by ID
    salereceipt = get_object_or_404(Sales_Receipt, id=salereceipt_id)
    # Fetch all products associated with this salereceipt
    salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=salereceipt)
    total_amount=salereceipt_products.aggregate(Sum('amount'))
    return render(request, 'sale/print_salereceipt.html', {
        'salereceipt': salereceipt,
        'salereceipt_products': salereceipt_products,
        'total_amount':total_amount
        
    })

def make_transaction(request,id):

    salereceipt_items_pro = {}
    total_amount = {}
    salereceipt = get_object_or_404(Sales_Receipt, id=id)
    print(salereceipt.customer_name,"ddd")
    salereceipts = Sales_Receipt.objects.all()

    for x in salereceipts:
        # Count the number of products for each sale receipt
        salereceipt_items_pro[x.id] = Sales_Receipt_Product.objects.filter(salereceipt=x).count()
        # Get products for the sale receipt and aggregate the amount
        salereceipt_products = Sales_Receipt_Product.objects.filter(salereceipt=x)
        total_amount[x.id] = salereceipt_products.aggregate(Sum('amount'))
    coname=salereceipt.customer_name
    print(coname,"eee")
    customer=Customer.objects.get(coname=coname, is_deleted=False)
    debit_account=Account.objects.get(customer=customer.id,is_deleted=False)
    credit_account=Account.objects.get(account_type="Revenue",name="Sales",is_deleted=False)
    amt=total_amount[id]
    print(amt)
    amount=amt['amount__sum']
    transaction=Transaction(description=f' sales receipt id = {salereceipt.id}',debit_account=debit_account,credit_account=credit_account,amount=amount)
    transaction.save()
    salereceipt.make_transaction=True
    salereceipt.save()
    salereceipts = Sales_Receipt.objects.all()
    messages.success(request, "Transaction added successfully!")

    return render(request, 'sale/list_sales.html', {
        'salereceipts': salereceipts,
        'salereceipt_items_pro': salereceipt_items_pro,
        'total_amount': total_amount
    })
