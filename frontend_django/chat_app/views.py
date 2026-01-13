import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from .ai_engine import get_answer  # Direct Import

@ensure_csrf_cookie
def home(request):
    """
    Renders the Brand Home page.
    """
    return render(request, 'chat_app/home.html')

@ensure_csrf_cookie
def chat_view(request):
    """
    Renders the chat interface and handles the proxy logic to FastAPI.
    """
    if request.method == 'POST':
        try:
            # Parse the JSON body from the frontend fetch call
            data = json.loads(request.body)
            question = data.get('question')
            
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            # Call AI Engine Directly (Single Server Mode)
            # This runs inside the Django process
            try:
                answer = get_answer(question)
                return JsonResponse({"answer": answer})
            except Exception as e:
                return JsonResponse({"error": f"AI Error: {str(e)}"}, status=500)

    # For GET requests, render the HTML template
    # Load product data from Database
    # For GET requests, render the HTML template
    # Load product data from Database
    from .models import Product, SiteConfig
    
    # Filter by Gender
    gender_filter = request.GET.get('gender')
    if gender_filter in ['Men', 'Women', 'Unisex']:
        products = Product.objects.filter(gender=gender_filter)
        selected_gender = gender_filter
    else:
        products = Product.objects.all()
        selected_gender = 'All'
    
    # Get Config
    config = SiteConfig.get_solo()

    return render(request, 'chat_app/chat.html', {
        'products': products, 
        'config': config, 
        'active_theme': config.active_theme,
        'selected_gender': selected_gender
    })

# --- Custom Admin / Dashboard Views ---
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ProductForm
from django.core.management import call_command
from .models import Product, SiteConfig  # Import Product and SiteConfig globally
import io

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def dashboard(request):
    products = Product.objects.all().order_by('-id')
    config = SiteConfig.get_solo()
    
    # Handle Theme Change
    if request.method == 'POST' and 'theme' in request.POST:
        new_theme = request.POST.get('theme')
        if new_theme in dict(SiteConfig.THEME_CHOICES):
            config.active_theme = new_theme
            config.save()
            messages.success(request, f"Theme updated to: {new_theme}")
            return redirect('dashboard')
            
    return render(request, 'chat_app/dashboard.html', {'products': products, 'config': config})

@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'chat_app/product_form.html', {'form': form, 'title': 'Add Product'})

@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'chat_app/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})

@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('dashboard')
    return render(request, 'chat_app/product_confirm_delete.html', {'product': product})

@user_passes_test(is_admin)
def trigger_sync(request):
    try:
        out = io.StringIO()
        call_command('sync_products', stdout=out)
        result = out.getvalue()
        
        if "WARNING" in result or "Could not update AI" in result:
             messages.warning(request, f"Database synced, but AI update failed: {result}")
        else:
             messages.success(request, "✅ Database Synced & AI Brain Refreshed Successfully!")
             
    except Exception as e:
        messages.error(request, f"Sync failed: {str(e)}")
    
    return redirect('dashboard')
