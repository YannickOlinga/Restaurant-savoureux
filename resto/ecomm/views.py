from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import MenuItem, Category, Cart, CartItem, Contact, Order, OrderItem, Reservation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from .decorators import anonymous_required
import json

@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {username} !")
                return redirect('menu')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@anonymous_required
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    categories = Category.objects.all()
    featured_items = MenuItem.objects.filter(is_available=True)[:6]
    context = {
        'categories': categories,
        'featured_items': featured_items,
    }
    return render(request, 'index.html', context)

@login_required
def menu(request):
    # Récupérer tous les articles disponibles
    items = MenuItem.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Filtrage par catégorie
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    # Recherche
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Tri
    sort = request.GET.get('sort', 'name')  # Par défaut, tri par nom
    if sort in ['name', '-name', 'price', '-price']:
        items = items.order_by(sort)
    
    # Pagination
    paginator = Paginator(items, 12)  # 12 items par page
    page = request.GET.get('page')
    items = paginator.get_page(page)
    
    context = {
        'categories': categories,
        'items': items,
    }
    return render(request, 'menu.html', context)

@login_required
def panier(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    total = cart.get_total()
    context = {
        'cart_items': items,
        'total': total,
    }
    return render(request, 'panier.html', context)

@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        # Encodage correct du message avec les caractères spéciaux
        message = "{} ajouté au panier!".format(menu_item.name)
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items(),
            'message': message
        }, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return JsonResponse({'removed': True})
    elif action == 'remove':
        cart_item.delete()
        cart_total = cart_item.cart.get_total()
        return JsonResponse({
            'removed': True,
            'cart_total': float(cart_total)
        })
    
    cart_item.save()
    return JsonResponse({
        'quantity': cart_item.quantity,
        'total': float(cart_item.get_total()),
        'cart_total': float(cart_item.cart.get_total())
    })

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if request.method == 'POST':
        # Créer la commande
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total(),
            delivery_address=request.POST.get('address'),
            phone_number=request.POST.get('phone')
        )
        
        # Créer les éléments de la commande
        for item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price=item.menu_item.price
            )
        
        # Vider le panier
        cart.cartitem_set.all().delete()
        
        messages.success(request, "Votre commande a été passée avec succès!")
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def make_reservation(request):
    if request.method == 'POST':
        reservation = Reservation.objects.create(
            user=request.user,
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            number_of_guests=request.POST.get('guests'),
            special_requests=request.POST.get('requests'),
            phone_number=request.POST.get('phone')
        )
        messages.success(request, "Votre réservation a été enregistrée!")
        return redirect('my_reservations')
    
    return render(request, 'make_reservation.html')

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_reservations.html', {'reservations': reservations})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        messages.success(request, "Votre message a été envoyé avec succès!")
        return redirect('contact')
        
    return render(request, 'contact.html')

# Vues du tableau de bord administrateur
def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    # Statistiques générales
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_orders = Order.objects.filter(status='pending').count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    
    # Commandes récentes
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Réservations du jour
    today_reservations = Reservation.objects.filter(date=datetime.today()).order_by('time')
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'pending_reservations': pending_reservations,
        'recent_orders': recent_orders,
        'today_reservations': today_reservations,
    }
    return render(request, 'dashboard/dashboard.html', context)

@user_passes_test(is_staff)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    return render(request, 'dashboard/orders.html', {'orders': orders})

@user_passes_test(is_staff)
def admin_reservations(request):
    reservations = Reservation.objects.all().order_by('-date', '-time')
    paginator = Paginator(reservations, 10)
    page = request.GET.get('page')
    reservations = paginator.get_page(page)
    return render(request, 'dashboard/reservations.html', {'reservations': reservations})

@user_passes_test(is_staff)
def admin_reservation_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    reservations = Reservation.objects.filter(
        date__range=[start, end]
    ).select_related('user')
    
    events = []
    for reservation in reservations:
        events.append({
            'id': reservation.id,
            'title': f"{reservation.user.username} - {reservation.number_of_guests} pers.",
            'start': f"{reservation.date}T{reservation.time}",
            'className': f"bg-{reservation.status}",
        })
    
    return JsonResponse(events, safe=False)

@user_passes_test(is_staff)
def admin_menu(request):
    items = MenuItem.objects.all().order_by('category', 'name')
    categories = Category.objects.all()
    return render(request, 'dashboard/menu.html', {'items': items, 'categories': categories})

@user_passes_test(is_staff)
@require_POST
def admin_menu_add(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    price = request.POST.get('price')
    category_id = request.POST.get('category')
    image = request.FILES.get('image')
    
    category = get_object_or_404(Category, id=category_id)
    
    item = MenuItem.objects.create(
        name=name,
        description=description,
        price=price,
        category=category,
        image=image
    )
    
    messages.success(request, "Article ajouté avec succès!")
    return redirect('admin_menu')

@user_passes_test(is_staff)
@require_POST
def admin_menu_edit(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    
    item.name = request.POST.get('name')
    item.description = request.POST.get('description')
    item.price = request.POST.get('price')
    item.category_id = request.POST.get('category')
    
    if 'image' in request.FILES:
        if item.image:
            default_storage.delete(item.image.path)
        item.image = request.FILES['image']
    
    item.save()
    
    messages.success(request, "Article modifié avec succès!")
    return redirect('admin_menu')

@user_passes_test(is_staff)
@require_POST
def admin_menu_delete(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    
    if item.image:
        default_storage.delete(item.image.path)
    
    item.delete()
    
    messages.success(request, "Article supprimé avec succès!")
    return redirect('admin_menu')

@user_passes_test(is_staff)
@require_POST
def admin_menu_availability(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    is_available = request.POST.get('is_available') == 'true'
    
    item.is_available = is_available
    item.save()
    
    return JsonResponse({'success': True})

@user_passes_test(is_staff)
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@user_passes_test(is_staff)
@require_POST
def update_reservation_status(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    status = request.POST.get('status')
    if status in dict(Reservation.STATUS_CHOICES):
        reservation.status = status
        reservation.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
