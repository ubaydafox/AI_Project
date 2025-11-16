import json
from datetime import datetime
import pytz

# JSON ফাইলগুলো data ফোল্ডার থেকে লোড করার ফাংশন
def load_data():
    try:
        with open('data/routine_data.json', 'r', encoding='utf-8') as f:
            routine = json.load(f)
        with open('data/course_info.json', 'r', encoding='utf-8') as f:
            courses = json.load(f)
        with open('data/faculty_info.json', 'r', encoding='utf-8') as f:
            faculty = json.load(f)
        return routine, courses, faculty
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e}")
        return [], {}, {}

# গ্লোবাল ডেটা লোড করা
routine_data, course_info, faculty_info = load_data()

# ==========================================================
# ফাংশন ১: বর্তমান ক্লাস খুঁজে বের করা
# ==========================================================
def get_current_class(target_batch="CSE-60D"): # আপনার ব্যাচ এখানে ডিফল্ট হিসাবে ব্যবহার করতে পারেন
    
    # সিলেট টাইমজোন (Asia/Dhaka) সেট করা
    sylhet_tz = pytz.timezone('Asia/Dhaka')
    now = datetime.now(sylhet_tz)
    
    day_mapping = {
        'Sunday': 'রবিবার', 'Monday': 'সোমবার', 'Tuesday': 'মঙ্গলবার', 
        'Wednesday': 'বুধবার', 'Thursday': 'বৃহস্পতিবার', 'Friday': 'শুক্রবার', 
        'Saturday': 'শনিবার'
    }
    current_day_english = now.strftime('%A')
    current_day_bengali = day_mapping.get(current_day_english, current_day_english)
    current_time_str = now.strftime('%I:%M %p') 
    current_time = datetime.strptime(current_time_str, '%I:%M %p').time()
    
    current_class = None
    
    for entry in routine_data:
        if entry['day'] == current_day_bengali and entry['batch'] == target_batch:
            
            try:
                start_time = datetime.strptime(entry['start_time'], '%I:%M %p').time()
                end_time = datetime.strptime(entry['end_time'], '%I:%M %p').time()
            except ValueError:
                # সময় ফরম্যাট ভুল হলে এড়িয়ে যাওয়া
                continue

            if start_time <= current_time < end_time:
                current_class = entry
                break
                
    if current_class:
        course_full_name = course_info.get(current_class['course_code'], "নাম জানা নেই")
        faculty_full_name = faculty_info.get(current_class['faculty_initial'], "নাম জানা নেই")
        
        return (
            f"✅ **বর্তমানে ক্লাস চলছে ({target_batch}):**\n"
            f"কোর্স: {course_full_name} ({current_class['course_code']})\n"
            f"শিক্ষক: {faculty_full_name} ({current_class['faculty_initial']})\n"
            f"রুম: {current_class['room']}\n"
            f"সময়: {current_class['start_time']} - {current_class['end_time']}"
        )
    else:
        return f"আজ, **{current_day_bengali}** {current_time_str} এ আপনার ({target_batch}) কোনো ক্লাস চলছে না।"

# ==========================================================
# ফাংশন ২: সাপ্তাহিক রুটিন তৈরি করা
# ==========================================================
def get_weekly_routine(target_batch):
    filtered_routine = [entry for entry in routine_data if entry['batch'] == target_batch]
    
    if not filtered_routine:
        return f"দুঃখিত, ব্যাচ **{target_batch}** এর কোনো রুটিন পাওয়া যায়নি।"
        
    routine_by_day = {}
    for entry in filtered_routine:
        day = entry['day']
        if day not in routine_by_day:
            routine_by_day[day] = []
        routine_by_day[day].append(entry)
        
    response = f"📅 **ব্যাচ {target_batch} এর সাপ্তাহিক রুটিন**\n"
    
    day_order = ['শনিবার', 'রবিবার', 'সোমবার', 'মঙ্গলবার', 'বুধবার', 'বৃহস্পতিবার', 'শুক্রবার']
    
    for day in day_order:
        if day in routine_by_day:
            response += f"\n**--- {day} ---**\n"
            sorted_classes = sorted(routine_by_day[day], key=lambda x: datetime.strptime(x['start_time'], '%I:%M %p'))
            
            for class_entry in sorted_classes:
                course_full_name = course_info.get(class_entry['course_code'], class_entry['course_code'])
                
                response += (
                    f"  🕰️ {class_entry['start_time']} - {class_entry['end_time']}\n"
                    f"  📚 {course_full_name} | রুম: {class_entry['room']} | শিক্ষক: {class_entry['faculty_initial']}\n"
                )
    
    return response

# ==========================================================
# ফাংশন ৩: শিক্ষকের তথ্য খুঁজে বের করা
# ==========================================================
def get_faculty_info(initial):
    full_name = faculty_info.get(initial.upper())
    if full_name:
        return f"👨‍🏫 **শিক্ষক পরিচিতি:**\nনাম: {full_name}\nইনিশিয়াল: {initial.upper()}\n"
    else:
        return f"দুঃখিত, ইনিশিয়াল **{initial.upper()}** এর জন্য কোনো শিক্ষকের তথ্য পাওয়া যায়নি।"

# ==========================================================
# ফাংশন ৪: কোর্সের তথ্য খুঁজে বের করা
# ==========================================================
def get_course_info(code):
    full_name = course_info.get(code.upper())
    if full_name:
        return f"📚 **কোর্স পরিচিতি:**\nকোর্স নাম: {full_name}\nকোর্স কোড: {code.upper()}\n"
    else:
        return f"দুঃখিত, কোর্স কোড **{code.upper()}** এর জন্য কোনো তথ্য পাওয়া যায়নি।"