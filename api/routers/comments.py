from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db, get_auth_user
from ..db.models import User, Comment

router = APIRouter(tags=["Comments"])


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    user: User = Depends(get_auth_user),
    db: Session = Depends(get_db),
):
    """Delete a comment"""

    # Get comment if it exists
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, "No comment was found for the specified id")
    
    # Ensure user is authorized to delete this comment
    if user.id != comment.creator_id:
        raise HTTPException(403)
    
    # Delete comment from the database
    db.delete(comment)
    db.commit()
