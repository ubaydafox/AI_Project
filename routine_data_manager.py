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
        with open('data/bus_info.json', 'r', encoding='utf-8') as f:
            bus = json.load(f)
        return routine, courses, faculty, bus
    except FileNotFoundError as e:
        print(f"Error: Data file not found - {e}")
        return [], {}, {}, []

# গ্লোবাল ডেটা লোড করা
routine_data, course_info, faculty_info, bus_info = load_data()

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

# ==========================================================
# ফাংশন ৫: বাসের সময়সূচী
# ==========================================================
def get_bus_schedule(query=None):
    if not bus_info:
        return "🚌 বর্তমানে কোনো বাসের তথ্য পাওয়া যায়নি।"
    
    results = []
    if query:
        query = query.strip().lower()
        for bus in bus_info:
            # Search in route details, route name, or bus no
            route_details = bus.get('route_details', '').lower()
            route_name = bus.get('route_name', '').lower()
            bus_no = bus.get('bus_no', '').lower()
            
            if query in route_details or query in route_name or query in bus_no:
                results.append(bus)
    else:
        results = bus_info

    if not results:
        return f"❌ '{query}' এর জন্য কোনো বাসের রুট পাওয়া যায়নি। দয়া করে বাসের শুরুর স্থান (Start Route) দিয়ে চেষ্টা করুন।"

    response = "🚌 **বিশ্ববিদ্যালয় বাস সময়সূচী:**\n"
    for bus in results:
        route_details = bus.get('route_details', 'N/A')
        
        # Highlight the query in route details if it exists
        if query and query in route_details.lower():
            # Case-insensitive replacement to preserve original case but add markdown
            import re
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            route_details = pattern.sub(lambda m: f"**__{m.group(0)}__**", route_details)

        response += (
            f"\n📍 **রুট:** {bus.get('route_name', 'N/A')} ({bus.get('departure_location', 'N/A')} ➡️ {bus.get('arrival_location', 'N/A')})\n"
            f"🚌 **বাস নং:** {bus.get('bus_no', 'N/A')} | 🏷️ **ধরন:** {bus.get('bus_type', 'N/A')}\n"
            f"🕒 **সময়:** {bus.get('departure_time', 'N/A')} (ছাড়বে) - {bus.get('arrival_time', 'N/A')} (পৌঁছাবে)\n"
            f"🛣️ **স্টপেজ:** {route_details}\n"
        )
    return response

# ==========================================================
# ফাংশন ৬: ডেটা সেভ করা এবং নতুন এন্ট্রি যোগ করা (Admin Only)
# ==========================================================

def save_routine_data(data):
    try:
        with open('data/routine_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving routine data: {e}")
        return False

def save_course_info(data):
    try:
        with open('data/course_info.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving course info: {e}")
        return False

def save_faculty_info(data):
    try:
        with open('data/faculty_info.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving faculty info: {e}")
        return False

def add_routine_entry(day, batch, start_time, end_time, course_code, room, faculty_initial):
    new_entry = {
        "day": day,
        "batch": batch,
        "start_time": start_time,
        "end_time": end_time,
        "course_code": course_code,
        "room": room,
        "faculty_initial": faculty_initial
    }
    routine_data.append(new_entry)
    if save_routine_data(routine_data):
        return "✅ রুটিন এন্ট্রি সফলভাবে যোগ করা হয়েছে!"
    else:
        return "❌ রুটিন সেভ করতে সমস্যা হয়েছে।"

def add_course_entry(code, full_name):
    if code.upper() in course_info:
        return f"⚠️ কোর্স কোড {code.upper()} ইতিমধ্যে বিদ্যমান।"
    
    course_info[code.upper()] = full_name
    if save_course_info(course_info):
        return f"✅ কোর্স '{full_name}' ({code.upper()}) সফলভাবে যোগ করা হয়েছে!"
    else:
        return "❌ কোর্স ইনফো সেভ করতে সমস্যা হয়েছে।"

def add_faculty_entry(initial, full_name):
    if initial.upper() in faculty_info:
        return f"⚠️ ইনিশিয়াল {initial.upper()} ইতিমধ্যে বিদ্যমান।"
        
    faculty_info[initial.upper()] = full_name
    if save_faculty_info(faculty_info):
        return f"✅ শিক্ষক '{full_name}' ({initial.upper()}) সফলভাবে যোগ করা হয়েছে!"
    else:
        return "❌ ফ্যাকাল্টি ইনফো সেভ করতে সমস্যা হয়েছে।"