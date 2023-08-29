from fastapi import APIRouter, HTTPException

from ..dependencies import DatabaseSession, AuthenticatedUser
from ..db.models import Comment

router = APIRouter(tags=["Comments"])


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    user: AuthenticatedUser,
    db: DatabaseSession,
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
