from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Book, BookCreate, BookUpdate

router = APIRouter()


@router.post("/", response_model=Book)
def create_item(
    *, session: SessionDep, book_in: BookCreate
) -> Any:
    """
    Create new book.
    """
    book = session.get(Book, book_in.id)
    if book:
        raise HTTPException(status_code=409, detail="Book with this id already exists")
    book = Book.model_validate(book_in, update={"on_loan": False})
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.delete("/{id}")
def delete_item(session: SessionDep, id: int) -> dict:
    """
    Delete a book.
    """
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"message": "Book deleted successfully", "book": book}


@router.get("/", response_model=list[Book])
def read_books(session: SessionDep) -> list[Book]:
    """
    Retrieve all books.
    """
    stmt = select(Book)
    results = session.exec(stmt)
    return results.all()


@router.patch("/{id}", response_model=Book)
def update_item(
    *, session: SessionDep, id: int, book_update: BookUpdate) -> Book:
    """
    Update a book.
    """
    book = session.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.update(book_update)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book



