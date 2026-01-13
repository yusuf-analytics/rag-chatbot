import json
import os
from django.core.management.base import BaseCommand
from chat_app.models import Product

class Command(BaseCommand):
    help = 'Syncs Django Product DB to backend_fastapi/sample_data.json for RAG ingestion'

    def handle(self, *args, **options):
        products = Product.objects.all()
        data = []
        
        for p in products:
            item = {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "attributes": {
                    "material": p.material,
                    "size": p.size,
                    "color": p.color,
                    "gender": p.gender,
                    "category": p.category
                },
                "price": float(p.price),
                "stock": p.stock,
                "image_url": p.image.url if p.image else ""
            }
            data.append(item)
            
        # Path to backend_fastapi/sample_data.json
        # File is in: frontend_django/chat_app/management/commands/sync_products.py
        # We need to go up 5 levels to get to rag_chatbot root
        
        current_file = os.path.abspath(__file__) # .../commands/sync_products.py
        commands_dir = os.path.dirname(current_file) # .../commands
        management_dir = os.path.dirname(commands_dir) # .../management
        chat_app_dir = os.path.dirname(management_dir) # .../chat_app
        frontend_dir = os.path.dirname(chat_app_dir) # .../frontend_django
        project_root = os.path.dirname(frontend_dir) # .../rag_chatbot
        
        json_path = os.path.join(project_root, 'backend_fastapi', 'sample_data.json')
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully synced {len(data)} products to {json_path}'))

        # 2. Trigger Internal AI Engine Rebuild
        try:
            from chat_app.ai_engine import rebuild_index
            self.stdout.write("Triggering Internal AI Index Rebuild...")
            
            success = rebuild_index()
            
            if success:
                self.stdout.write(self.style.SUCCESS('✅ AI Brain Updated Successfully (Internal)!'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ AI Rebuild verification returned False.'))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not update AI Index: {e}'))
