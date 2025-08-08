import json
import os
import shutil

# The JSON data provided by the user
json_data = '''
[
    {"idx":0,"id":"1784f69a-fc86-41c9-b272-bda489fdb310","name":"English","description":"Study living organisms and their interactions with the environment","icon_url":"leaf","color_code":"#059669","order":4,"is_active":true,"class_id":"ef76faf5-707e-4387-9b7b-4b4894b6b548"},
    {"idx":1,"id":"19556cf1-b588-4d80-9cde-e104a754820d","name":"English","description":null,"icon_url":null,"color_code":null,"order":null,"is_active":true,"class_id":"8b9e97d4-2f6a-4794-b525-3c7f8a20730d"},
    {"idx":2,"id":"4eb90d55-96db-47ee-8f83-386c5167555b","name":"Mathematics","description":null,"icon_url":null,"color_code":null,"order":null,"is_active":true,"class_id":"ef76faf5-707e-4387-9b7b-4b4894b6b548"},
    {"idx":3,"id":"52fd640a-26f7-4a18-8da1-c515649dc51e","name":"Mathematics","description":null,"icon_url":null,"color_code":null,"order":null,"is_active":true,"class_id":"6c4db2d7-7ad4-4c87-90f6-b65b28b57a56"},
    {"idx":4,"id":"553eecfa-bd07-472d-a837-d8fc7807560f","name":"Physics","description":"Explore the laws of motion, energy, and the fundamental forces of nature","icon_url":"flash","color_code":"#F97316","order":2,"is_active":true,"class_id":"8b9e97d4-2f6a-4794-b525-3c7f8a20730d"},
    {"idx":5,"id":"70144aef-f8c9-4abd-8fa4-e9f471377f4c","name":"Mathematics","description":"Master fundamental mathematical concepts and problem-solving skills","icon_url":"calculator","color_code":"#4F46E5","order":1,"is_active":true,"class_id":"8b9e97d4-2f6a-4794-b525-3c7f8a20730d"},
    {"idx":6,"id":"ab0d5ed3-c195-4b29-9c8e-93917cf8036d","name":"English","description":null,"icon_url":null,"color_code":null,"order":null,"is_active":true,"class_id":"6c4db2d7-7ad4-4c87-90f6-b65b28b57a56"},
    {"idx":7,"id":"f439132a-2904-4b4e-a886-8b18cc71e8e1","name":"Chemistry","description":"Learn about elements, compounds, and chemical reactions","icon_url":"flask","color_code":"#10B981","order":3,"is_active":true,"class_id":"ef76faf5-707e-4387-9b7b-4b4894b6b548"}
]
'''

def move_subject_files():
    """Moves files from math and vocab directories to the new structure."""
    data = json.loads(json_data)
    base_path = 'maindata'
    dest_base_path = os.path.join(base_path, 'dailtpractise')

    subject_map = {
        'Mathematics': 'math',
        'English': 'vocab'
    }

    for item in data:
        subject_name = item.get('name')
        class_id = item.get('class_id')
        subject_id = item.get('id')

        if subject_name in subject_map and class_id and subject_id:
            source_folder_name = subject_map[subject_name]
            source_dir = os.path.join(base_path, source_folder_name, class_id)
            dest_dir = os.path.join(dest_base_path, class_id, subject_id, 'pdfs')

            if os.path.isdir(source_dir):
                for filename in os.listdir(source_dir):
                    source_file = os.path.join(source_dir, filename)
                    if os.path.isfile(source_file):
                        try:
                            shutil.move(source_file, dest_dir)
                            print(f'Moved {filename} to {dest_dir}')
                        except (shutil.Error, OSError) as e:
                            print(f'Error moving {filename}: {e}')
            else:
                print(f'Source directory not found: {source_dir}')

if __name__ == '__main__':
    move_subject_files()
