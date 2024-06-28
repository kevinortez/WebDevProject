from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from bookMng.models import MainMenu, Book, BookRating, CartItem, Favorite
from .forms import BookForm, RateBook, ToggleFavorite


# Create your views here.


def index(request):
    return render(request,
                  'bookMng/index.html',
                  {
                      'item_list': MainMenu.objects.all()
                  }
                  )

def home(request):
    return render(request,
                  'bookMng/home.html',
                  {
                      'item_list': MainMenu.objects.all()
                  }
                  )

def aboutus(request):
    return render(request,
                  'bookMng/about_us.html',
                  {
                      'item_list': MainMenu.objects.all()
                  }
                  )


def displaybooks(request):
    books = Book.objects.all()
    book_ratings = []
    for book in books:
        book.pic_path = book.picture.url[14:]
        ratings = BookRating.objects.filter(book_id=book.id)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        favorite = Favorite.objects.filter(book_id=book.id, user_id=request.user).first()
        book_ratings.append((book, avg_rating, favorite))
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book_list': book_ratings,
                  }
                  )


def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            try:
                book.username = request.user
            except Exception:
                pass
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request,
                  'bookMng/postbook.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'submitted': submitted,
                  }
                  )


def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    book.pic_path = book.picture.url[14:]
    ratings = BookRating.objects.filter(book_id=book_id)
    num_ratings = BookRating.objects.filter(book_id=book_id).count()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    rating_list = [0, 0, 0, 0, 0]
    rating_list_percent = [0, 0, 0, 0, 0]
    for r in ratings:
        rating_list[r.rating - 1] = rating_list[r.rating - 1] + 1
    for x in range(0, 5):
        if num_ratings == 0:
            rating_list_percent[x] = 0
        else:
            rating_list_percent[x] = (rating_list[x]/num_ratings)*100
    return render(request,
                  'bookMng/book_detail.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'num_ratings': num_ratings,
                      'avg_rating': avg_rating,
                      'rating_list': rating_list,
                      'rating_list_percent': rating_list_percent
                  }
                  )


def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book_list': books,
                  }
                  )


def book_delete(request, book_id):
    book = Book.objects.get(id=book_id)
    book.delete()
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request,
                  'bookMng/mybooks.html',
                  {
                      'item_list': MainMenu.objects.all(),
                      'book': book,
                      'book_list': books,
                  }
                  )


def search(request):
        name=request.GET.get('search')
        books = Book.objects.filter(name__icontains=name)
        book_ratings = []
        for book in books:
            book.pic_path = book.picture.url[14:]
            ratings = BookRating.objects.filter(book_id=book.id)
            avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            favorite = Favorite.objects.filter(book_id=book.id, user_id=request.user).first()
            book_ratings.append((book, avg_rating, favorite))
        return render(request,
                      'bookMng/displaybooks.html',
                      {
                          'item_list': MainMenu.objects.all(),
                          'book_list': book_ratings,
                      }
                      )


def ratebook(request):
    books = Book.objects.all()
    book_ratings = []
    for book in books:
        book.pic_path = book.picture.url[14:]
        ratings = BookRating.objects.filter(book_id=book.id)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        book_ratings.append((book, avg_rating))
    if request.method == 'POST':
        form = RateBook(request.POST)
        if form.is_valid():
            rate = form.save(commit=False)
            try:
                rate.user_id = request.user
            except Exception:
                pass
            # Check if there is already a rating for the book by the user
            existing_rating = BookRating.objects.filter(book_id=rate.book_id, user_id=rate.user_id).first()
            if existing_rating:
                # Update the existing rating
                existing_rating.rating = rate.rating
                existing_rating.save()
                return HttpResponseRedirect('/displaybooks')
            rate.save()
            return HttpResponseRedirect('/displaybooks')
    else:
        form = RateBook()
    return render(request,
                  'bookMng/displaybooks.html',
                  {
                      'form': form,
                      'item_list': MainMenu.objects.all(),
                      'book_list': book_ratings,
                  }
                  )


def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity', 0)
        cart_item, created = CartItem.objects.get_or_create(book=book, user=request.user)
        cart_item.quantity += int(quantity)
        cart_item.save()
        return HttpResponseRedirect('/cart')
    return render(request, 'cart', {'book': book})


def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    for c in cart_items:
        c.book.pic_path = c.book.picture.url[14:]
    return render(request, 'bookMng/shopping_cart_summary.html',
                  {'cart_items': cart_items,
                   'total_price': total_price,
                   'item_list': MainMenu.objects.all(),
                   })


def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if request.method == 'POST':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    return HttpResponseRedirect('/cart')


def shopping_cart_summary(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.book.price * item.quantity for item in cart_items)
    for c in cart_items:
        c.book.pic_path = c.book.picture.url[14:]
    return render(request, "shopping_cart_summary.html",
                  {'cart_item': cart_items,
                   'total_price': total_price,
                   'item_list': MainMenu.objects.all(),
                   })


def favorite(request):
    if request.method == 'POST':
        book = Book.objects.get(id=request.POST.get('book_id'))
        user = request.user
        favorite = Favorite.objects.filter(book_id=book, user_id=user).first()
        if favorite:
            favorite.is_favorite = not favorite.is_favorite
            favorite.save()
        else:
            Favorite.objects.create(book_id=book, user_id=user, is_favorite=True)
    return HttpResponseRedirect('/displaybooks')


def my_favorites(request):
    fav_books = Favorite.objects.filter(user_id=request.user, is_favorite=True)
    for b in fav_books:
        b.book_id.pic_path = b.book_id.picture.url[14:]
    return render(request,
                  "bookMng/my_favorites.html",
                  {
                      'item_list': MainMenu.objects.all(),
                      'book_list': fav_books
                  }
                  )

class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)



