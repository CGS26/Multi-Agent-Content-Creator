from typing import List, Dict, Any, Optional
from models.lessons import lessons
from models.content.text import TextContent
from logger.config import logger
import uuid


class DataTransformer:
    """
    Agent responsible for transforming structured content data into lesson objects
    """
    
    def __init__(self):
        logger.info("DataTransformer agent initialized")
    
    def transform_sections_to_lessons(self, structured_sections: List, 
                                    course_id: Optional[str] = None) -> List[lessons]:
        """
        Transform structured sections into lesson objects
        
        Args:
            structured_sections: List of ContentUnion objects (TextContent instances)
            course_id: UUID string for course_id (optional, will generate if not provided)
            
        Returns:
            List[lessons]: List of lesson objects (single lesson with all sections)
        """
        try:
            logger.info(f"Transforming {len(structured_sections)} structured sections to a single lesson")
            
            if course_id is None:
                course_id = str(uuid.uuid4())
                logger.info(f"Generated course_id: {course_id}")
            
            lesson = lessons(
                course_id=uuid.UUID(course_id),
                title="Mathematics Lesson", 
                is_active=True,
                sections=structured_sections  
            )
            
            logger.info(f"Successfully created single lesson with {len(structured_sections)} sections")
            return [lesson]
            
        except Exception as e:
            logger.error(f"Error transforming sections to lessons: {e}")
            raise
    
    def _group_sections_by_title(self, structured_sections: List) -> Dict[str, List]:
        """
        Group sections by their title to create logical lessons
        
        Args:
            structured_sections: List of ContentUnion objects (TextContent instances)
            
        Returns:
            Dict[str, List]: Sections grouped by title
        """
        try:
            lesson_groups = {}
            
            for section in structured_sections:
                title = section.title if hasattr(section, 'title') else "Untitled"
                
                # Clean up title for better grouping
                clean_title = self._clean_lesson_title(title)
                
                if clean_title not in lesson_groups:
                    lesson_groups[clean_title] = []
                
                lesson_groups[clean_title].append(section)
            
            logger.debug(f"Grouped sections into {len(lesson_groups)} lessons")
            return lesson_groups
            
        except Exception as e:
            logger.error(f"Error grouping sections by title: {e}")
            raise
    
    def _clean_lesson_title(self, title: str) -> str:
        """
        Clean and standardize lesson titles
        
        Args:
            title: Raw title string
            
        Returns:
            str: Cleaned title
        """
        try:
            title = title.strip()
            
            if len(title) > 100:
                title = title[:97] + "..."
            
            if not title:
                title = "Untitled Lesson"
            
            return title
            
        except Exception as e:
            logger.error(f"Error cleaning lesson title: {e}")
            return "Untitled Lesson"
    
    def validate_lesson_data(self, lesson: lessons) -> bool:
        """
        Validate lesson data before SQL generation
        
        Args:
            lesson: lessons object to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not lesson.title or len(lesson.title.strip()) == 0:
                logger.warning("Lesson title is empty")
                return False
            
            if not lesson.sections or len(lesson.sections) == 0:
                logger.warning(f"Lesson '{lesson.title}' has no sections")
                return False
            
            for i, section in enumerate(lesson.sections):
                if not section.content or len(section.content.strip()) == 0:
                    logger.warning(f"Section {i} in lesson '{lesson.title}' has empty content")
                    return False
                
                if not section.title or len(section.title.strip()) == 0:
                    logger.warning(f"Section {i} in lesson '{lesson.title}' has empty title")
                    return False
            
            logger.debug(f"Lesson '{lesson.title}' validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating lesson data: {e}")
            return False 