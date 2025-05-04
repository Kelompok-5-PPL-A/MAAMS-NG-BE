from django.core.management.base import BaseCommand
from question.models import Question
from cause.models import Causes
from tag.models import Tag
import uuid

class Command(BaseCommand):
    help = 'Seed the Causes model with well-defined data for server environments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding causes for server environment...'))

        question_data = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Root Cause Analysis Question",
                "mode": "PRIBADI",
                "tags": ["test", "data", "seeding"]
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Performance Bottleneck Analysis",
                "mode": "PENGAWASAN",
                "tags": ["test", "data", "seeding"]             
            }
        ]

        questions = {}
        for qdata in question_data:
            question_params = qdata.copy()

            tags_list = question_params.pop("tags") if "tags" in question_params else []
            
            # Create or update the Question without tags
            question, created = Question.objects.update_or_create(
                id=uuid.UUID(question_params["id"]),
                defaults={
                    "title": question_params["title"],
                    "mode": question_params["mode"],
                }
            )
            
            question.tags.clear()
            for tag_name in tags_list:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)
            
            questions[question_params["id"]] = question
            
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} question: {question.title}")
            
        # Predefined causes for consistent testing
        causes_data = [
            {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "row": 0,
                "column": 0,
                "mode": Causes.ModeChoices.PRIBADI,
                "cause": "Hardware failure in primary system",
                "status": True,
                "root_status": True,
                "feedback": "Critical issue"
            },
            {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "row": 0,
                "column": 1,
                "mode": Causes.ModeChoices.PRIBADI,
                "cause": "Software configuration error",
                "status": True,
                "root_status": False,
                "feedback": "Secondary issue"
            },
            {
                "id": "660e8400-e29b-41d4-a716-446655440002",
                "question_id": "550e8400-e29b-41d4-a716-446655440001",
                "row": 0,
                "column": 0,
                "mode": Causes.ModeChoices.PENGAWASAN,
                "cause": "Database query optimization needed",
                "status": True,
                "root_status": True,
                "feedback": "High priority"
            }
        ]
        
        for cdata in causes_data:
            _, created = Causes.objects.update_or_create(
                id=uuid.UUID(cdata["id"]),
                defaults={
                    "question": questions[cdata["question_id"]],
                    "row": cdata["row"],
                    "column": cdata["column"],
                    "mode": cdata["mode"],
                    "cause": cdata["cause"],
                    "status": cdata["status"],
                    "root_status": cdata["root_status"],
                    "feedback": cdata["feedback"]
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} cause: {cdata['cause']}")
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded causes for server environment'))