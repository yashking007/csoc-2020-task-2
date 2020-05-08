from django.shortcuts import render
from django.shortcuts import get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
    return render(request, 'store/index.html')

def bookDetailView(request, bid):
    template_name = 'store/book_detail.html'
    context = {
        'book': get_object_or_404( Book, id__exact=bid ), # set this to an instance of the required book
        'num_available': BookCopy.objects.filter(book__id__exact=bid, status__exact=True).count(), # set this to the number of copies of the book available, or 0 if the book isn't available
    }
    # START YOUR CODE HERE
    
    
    return render(request, template_name, context=context)


@csrf_exempt
def bookListView(request):
    template_name = 'store/book_list.html'
    get_data = request.GET
    
    try:
        books = Book.objects.filter(
            title__contains=get_data['title'],
            author__contains=get_data['author'],
            genre__contains=get_data['genre'],
        )
    except:
        books = Book.objects.all()
    
    context = {
        'books': books, # set this to the list of required books upon filtering using the GET parameters
                       # (i.e. the book search feature will also be implemented in this view)
    }
    
    # START YOUR CODE HERE
    
    
    return render(request, template_name, context=context)

@login_required
def viewLoanedBooks(request):
    template_name = 'store/loaned_books.html'
    context = {
        'books': BookCopy.objects.filter(status__exact=False, borrower = request.user),
    }
    '''
    The above key 'books' in the context dictionary should contain a list of instances of the 
    BookCopy model. Only those book copies should be included which have been loaned by the user.
    '''
    # START YOUR CODE HERE
    


    return render(request, template_name, context=context)

@csrf_exempt
@login_required
def loanBookView(request):
    post_data = request.POST
    books = BookCopy.objects.filter( book__id__exact=post_data['bid'], status__exact=True )
    
    if len(books):
        message = 'success'
        books[0].status = False
        books[0].borrower = request.user
        books[0].save()
    else :
        message = 'failure'
    
    response_data = {
        'message': message,
    }
    '''
    Check if an instance of the asked book is available.
    If yes, then set the message to 'success', otherwise 'failure'
    '''
    # START YOUR CODE HERE
    #book_id = None# get the book id from post data


    return JsonResponse(response_data)

'''
FILL IN THE BELOW VIEW BY YOURSELF.
This view will return the issued book.
You need to accept the book id as argument from a post request.
You additionally need to complete the returnBook function in the loaned_books.html file
to make this feature complete
''' 
@csrf_exempt
@login_required
def returnBookView(request):
    post_data = request.POST
    try:
        bookCopy = BookCopy.objects.get( id__exact=post_data['bid'], borrower=request.user )
        message = 'success'
        bookCopy.status = True
        bookCopy.borrower = None
        bookCopy.save()
    except:
        message = 'failure'
    
    response_data = {
        'message': message
    }
    return JsonResponse(response_data)

@csrf_exempt
@login_required
def rateBookView(request):
    post_data = request.POST
    book = get_object_or_404(Book, pk=post_data['bid'])
    response = {'message':'failure'}
    if post_data['rating']>10 or post_data['rating']<0:
        return JsonResponse(response)
    try :
        new_rating = BookRating.objects.get(user=request.user, book=book)
        new_rating.rating = post_data['rating']
    except:
        new_rating = BookRating(user=request.user, book=book, rating=post_data['rating'])
    new_rating.save()

    book_ratings = BookRating.objects.filter(book=book)
    sum=0
    for book_rating in book_ratings:
        sum += book_rating.rating
    avg = sum/book_ratings.count()
    book.rating = avg
    book.save()
    response = {'message':'success', 'overall':avg}
    return JsonResponse(response)