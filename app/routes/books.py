from fastapi import APIRouter, Request, Query, Depends
from ..models import Book
from ..database import get_db
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/books")
def get_books(request: Request, page: int = Query(1, alias="page", ge=1), db: Session = Depends(get_db)):
    books_per_page = 10
    total_books = db.query(Book).count()
    books = db.query(Book).offset((page - 1) * books_per_page).limit(books_per_page).all()

    return templates.TemplateResponse("books_list.html", {
        "request": request,
        "books": books,
        "page": page,
        "has_next": total_books > page * books_per_page,
        "has_prev": page > 1
    })
@router.get("/books/{id}")
def get_book(request: Request, id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return templates.TemplateResponse("book_detail.html", {"request": request, "book": book})

@router.get("/books/new")
def new_book_form(request: Request):
    return templates.TemplateResponse("book_form.html", {"request": request})



@router.post("/books")
def create_book(
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    total_pages: int = Form(...),
    genre: str = Form(...),
    db: Session = Depends(get_db)
):
    new_book = Book(title=title, author=author, year=year, total_pages=total_pages, genre=genre)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return RedirectResponse(url="/books", status_code=303)


@router.get("/books/{id}/edit")
def edit_book_form(request: Request, id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    return templates.TemplateResponse("book_edit_form.html", {"request": request, "book": book})
from fastapi import Form, HTTPException

@router.post("/books/{id}/edit")
def update_book(
    id: int,
    title: str = Form(...),
    author: str = Form(...),
    year: int = Form(...),
    total_pages: int = Form(...),
    genre: str = Form(...),
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = title
    book.author = author
    book.year = year
    book.total_pages = total_pages
    book.genre = genre

    db.commit()
    db.refresh(book)

    return RedirectResponse(url=f"/books/{book.id}", status_code=303)

@router.post("/books/{id}/delete")
def delete_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()

    return RedirectResponse(url="/books", status_code=303)
