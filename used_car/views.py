from django.shortcuts import render
from django.db.models import Sum, Q
# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import UsedCar,charges,Customer, Brand, Payments
from .forms import UsedCarForm, ChargesForm, CustomerForm, PaymentsForm
from .tables import UsedCarTable, CustomerTable, PaymentsTable, SoldUsedCarTable
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django_tables2 import RequestConfig
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from datetime import date, timedelta
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from django.views import View
from django.utils import timezone


@login_required
def used_car_detail(request, pk):
    used_car = get_object_or_404(UsedCar, pk=pk)
    return render(request, 'used_car/usedcar_detail.html', {'used_car': used_car})


@login_required
def used_car_create(request):
    default_date = date.today().strftime('%Y-%m-%d')
    brands = Brand.objects.all() 
    if request.method == 'POST':
        form = UsedCarForm(request.POST)
        if form.is_valid():
            form.save()
            queryset = UsedCar.objects.filter(status='available')
            table = UsedCarTable(queryset)
            RequestConfig(request).configure(table)
            return render(request, 'used_car/usedcar_list.html', {'table': table, 'default_date': default_date, 'title': "Cars/Bikes"})
        else:
            print(form.errors)
    else:
        form = UsedCarForm(initial={'purchased_date': default_date})
    return render(request, 'used_car/usedcar_create.html', {'form': form, 'default_date': default_date, 'brands': brands})


@login_required
def used_car_edit(request, pk):
       used_car = get_object_or_404(UsedCar, pk=pk)
       if request.method == 'POST':
                form = UsedCarForm(request.POST, instance=used_car)
                if form.is_valid():
                    form.save()
                    return redirect('usedcar:used_car_list')
       else:
                form = UsedCarForm(instance=used_car)  
                return render(request, 'used_car/usedcar_edit.html', {'form': form})

    

@login_required
class UsedCarDeleteView(View):
    def post(self, request, pk):
        used_car = get_object_or_404(UsedCar, pk=pk)
        used_car.delete()
        return redirect('usedcar:used_car_list')


@login_required
def used_car_list(request):
    search_query = request.GET.get('q')

    if search_query:
        queryset = UsedCar.objects.filter(vehicle_name__icontains=search_query)
    else:
        queryset = UsedCar.objects.filter(status='available').order_by('vehicle_name')

    queryset = queryset.annotate(total_expense=Sum('charges__spares') + Sum('charges__labour'))

    items_per_page = 10
    paginator = Paginator(queryset, items_per_page)
    page = request.GET.get('page')
    try:
        all_cars = paginator.page(page)
    except PageNotAnInteger:
        all_cars = paginator.page(1)
    except EmptyPage:
        all_cars = paginator.page(paginator.num_pages)

    table = UsedCarTable(all_cars)
    RequestConfig(request, paginate={'per_page': items_per_page}).configure(table)

    return render(request, 'used_car/usedcar_list.html', {'table': table, 'all_cars': all_cars, 'title': 'Cars/Bikes'})


@login_required
def sold_list(request):

    queryset = UsedCar.objects.filter(status='sold')

    queryset = queryset.annotate(total_expense=Sum('charges__spares') + Sum('charges__labour'))

    items_per_page = 10
    paginator = Paginator(queryset, items_per_page)
    page = request.GET.get('page')
    try:
        all_cars = paginator.page(page)
    except PageNotAnInteger:
        all_cars = paginator.page(1)
    except EmptyPage:
        all_cars = paginator.page(paginator.num_pages)

    table = SoldUsedCarTable(all_cars)
    RequestConfig(request, paginate={'per_page': items_per_page}).configure(table)

    return render(request, 'used_car/usedcar_list.html', {'table': table, 'all_cars': all_cars, 'title': 'Closed Deals'})

@login_required
def charges_list(request):
    charges_list = charges.objects.all()
    return render(request, 'used_car/charges_list.html', {'charges_list': charges_list})


@login_required
def create_charges(request, pk):
    used_car = get_object_or_404(UsedCar, pk=pk)
    charges_entries = charges.objects.filter(used_car=used_car)

    paginator = Paginator(charges_entries, 10)  # Show 10 charges per page

    page_number = request.GET.get('page')
    charges_entries = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ChargesForm(request.POST)
        if form.is_valid():
            charges_instance = form.save(commit=False)
            charges_instance.used_car = used_car
            charges_instance.save()
            return redirect('usedcar:used_car_list')
    else:
        form = ChargesForm()

    return render(request, 'used_car/create_charges.html', {'form': form, 'used_car': used_car, 'charges_entries': charges_entries})





@login_required
def delete_charges(request, pk):
    entry = get_object_or_404(charges, pk=pk)
    used_car = entry.used_car  
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Charge entry has been deleted successfully.')
        return redirect('usedcar:create_charges', pk=used_car.pk) 
    return render(request, 'used_car/create_charges.html', {'used_car': used_car})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('usedcar:used_car_list')  
        else:
            error_message = "Invalid username or password."
            return render(request, 'used_car/login.html', {'error_message': error_message})
    else:
        return render(request, 'used_car/login.html')
  
  
def logout_view(request):
    logout(request)
    return redirect('usedcar:login')  

import plotly.graph_objs as go

def pie_chart_view(request):
    expenses = charges.objects.all()
    total_spares = sum(expense.spares for expense in expenses)
    total_labour = sum(expense.labour for expense in expenses)

    # Create the pie chart
    labels = ['Spares', 'Labour']
    values = [total_spares, total_labour]
    colors = ['#1f77b4', '#ff7f0e']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])

    # Convert the chart to HTML
    plot_div = fig.to_html(full_html=False)

    context = {'plot_div': plot_div}
    return render(request, 'used_car/pie_chart.html', context)

@login_required
def add_customer(request):
    form = CustomerForm()
    used_cars = UsedCar.objects.filter(status='available')
    
    interested_vehicle_id = request.GET.get('interested_vehicle')
    advance_amount = request.GET.get('advance_amount')
    name = request.GET.get('name')
    contact = request.GET.get('contact')
    address = request.GET.get('address')
    sell_price = request.GET.get('sell_price')
    aadhar_no = request.GET.get('aadhar_no')
        
    if interested_vehicle_id and advance_amount and name and contact and address and sell_price and aadhar_no:
        form = CustomerForm(initial={
            'interested_vehicle': interested_vehicle_id,
            'advance_amount': advance_amount,
             'name': name,
            'contact': contact,
            'address': address,
            'aadhar_no' : aadhar_no,
            'sell_price': sell_price
        })
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            interested_vehicle = form.cleaned_data['interested_vehicle']
            interested_vehicle.status = 'advanced'
            interested_vehicle.save()
            return redirect('usedcar:customer_list')
        else:
            print(form.errors)
    
    return render(request, 'used_car/add_customer.html', {'form': form, 'used_cars': used_cars})





@login_required
def customer_list(request):
    customer_list = Customer.objects.filter(interested_vehicle__status='advanced')
    table = CustomerTable(customer_list)
    return render(request, 'used_car/customer_list.html', {'table': table})


class BrandListView(ListView):
    model = Brand
    template_name = 'used_car/brand_list.html'
    context_object_name = 'brands'


class AddBrandView(CreateView):
    model = Brand
    fields = ['brand_name', 'model_name', 'yom']
    template_name = 'used_car/add_brand.html'
    success_url = '/brand_list/' 
    
class BrandUpdate(UpdateView):
    model = Brand
    fields = ['brand_name', 'model_name', 'yom']
    template_name = 'used_car/add_brand.html'
    success_url ='/brand_list/'     
    
@login_required
def add_payments(request, pk):
    transaction_car = get_object_or_404(Customer, pk=pk)
    charges_entries = Payments.objects.filter(transaction_car=transaction_car)

    paginator = Paginator(charges_entries, 10)  # Show 10 charges per page

    page_number = request.GET.get('page')
    charges_entries = paginator.get_page(page_number)

    if request.method == 'POST':
        form = PaymentsForm(request.POST)
        if form.is_valid():
            charges_instance = form.save(commit=False, transaction_car=transaction_car)
            # charges_instance.transaction_car = transaction_car
            charges_instance.save()
            payments = Payments.objects.filter(transaction_car=transaction_car).aggregate(Sum('amount'))['amount__sum'] or 0.0
            total_paid = float(payments) + float(transaction_car.advance_amount)
            if total_paid >= float(transaction_car.sell_price):
                transaction_car.interested_vehicle.status = 'sold'
                transaction_car.interested_vehicle.save()
            
            return redirect('usedcar:customer_list')
    else:
        form = PaymentsForm()

    customer_list = Customer.objects.all()
    table = PaymentsTable(customer_list)
    return render(request, 'used_car/add_payments.html', {'form': form, 'transaction_car': transaction_car, 'charges_entries': charges_entries})

@login_required
def sales_update(request, customer_id):
       customer = get_object_or_404(Customer, pk=customer_id)
       if request.method == 'POST':
                form = CustomerForm(request.POST, instance=customer)
                if form.is_valid():
                    form.save()
                    return redirect('usedcar:customer_list')
       else:
                form = CustomerForm(instance=customer)  
                return render(request, 'used_car/customer_update.html', {'form': form})
            
            
@login_required
def dashboard(request):
    total_cars = UsedCar.objects.count()
    available_cars = UsedCar.objects.filter(status='available').count()
    advanced_cars = UsedCar.objects.filter(status='advanced').count()
    sold_cars = UsedCar.objects.filter(status='sold').count()
    total_capital = UsedCar.objects.aggregate(purchased_price=Sum('purchased_price'))['purchased_price']
    days_range = 30
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_range)
    
    total_sell_price = Customer.objects.filter(
        interested_vehicle__status='sold',
        interested_vehicle__purchased_date__range=(start_date, end_date)
    ).aggregate(total_sell_price=Sum('sell_price'))['total_sell_price'] or 0
    
    # sold_cars_filtered = UsedCar.objects.filter(status='sold', purchased_date__range=(start_date, end_date))
    # total_sell_price = Customer.objects.filter(
    #     interested_vehicle__in=sold_cars_filtered
    # ).aggregate(total_sell_price=Sum('sell_price'))['total_sell_price'] or 0
    
    # total_advance = Customer.objects.filter(
    #     interested_vehicle__in=sold_cars_filtered
    # ).aggregate(advance_amount=Sum('advance_amount'))['advance_amount']
    
    # total_payments = Payments.objects.filter(
    #     transaction_car__interested_vehicle__in=sold_cars_filtered
    # ).aggregate(amount=Sum('amount'))['amount']

    
    # total_sell_price = Customer.objects.aggregate(total_sell_price=Sum('sell_price'))['total_sell_price']
    
    total_advance = Customer.objects.aggregate(advance_amount=Sum('advance_amount'))['advance_amount']
    total_payments = Payments.objects.aggregate(amount=Sum('amount'))['amount']
    
    
    results = {
        'total_cars':total_cars , 
        'available_cars': available_cars, 
        'advanced_cars': advanced_cars, 
        'sold_cars': sold_cars, 
        'total_sell_price':total_sell_price,
        'total_capital': int(total_capital),
        'payment': total_advance + total_payments,
        'payment_due': total_sell_price - (total_advance + total_payments)
    }

    return render(request, 'used_car/pie_chart.html', results)



class PageView(TemplateView):
    template_name = "used_car/detail_view.html"

    def get_context_data(self, **kwargs):
        # 
        context = super().get_context_data(**kwargs)
        context['used_cars'] = UsedCar.objects.filter(pk=self.kwargs['pk'])
        context['expenses'] = charges.objects.filter(used_car__id=self.kwargs['pk'])
        context["customers"] = Customer.objects.filter(interested_vehicle__id=self.kwargs['pk'])
        context["payments"] = Payments.objects.filter(transaction_car__id=self.kwargs['pk'])
        return context