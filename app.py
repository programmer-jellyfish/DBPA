from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Reports storage configuration
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
REPORTS_FILE = os.path.join(REPORTS_DIR, 'reports.json')

# Create reports directory if it doesn't exist
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)
    print(f"✓ Created reports directory: {REPORTS_DIR}")

# Load or initialize reports storage
def load_reports():
    """Load reports from JSON file."""
    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading reports: {e}")
            return {"reports": []}
    return {"reports": []}

def save_reports(data):
    """Save reports to JSON file."""
    try:
        with open(REPORTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving reports: {e}")
        return False

# Load dataset at startup
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'Smartphone_Usage_Productivity_Dataset_50000.csv')
try:
    dataset_df = pd.read_csv(DATASET_PATH)
    print(f"✓ Dataset loaded: {len(dataset_df)} records")
    print(f"  Columns: {', '.join(dataset_df.columns.tolist())}")
except FileNotFoundError:
    print(f" Dataset not found at {DATASET_PATH}")
    dataset_df = None
except Exception as e:
    print(f" Error loading dataset: {e}")
    dataset_df = None

class DBPAAnalysisEngine:
    """Digital Behaviour Productivity Analysis Engine"""
    
    @staticmethod
    def calculate_stress_index(sleep_hours, screen_hours, work_hours, social_media, meal_quality, average_score, procrastination, attention_span):
        """
        Calculate stress index based on daily habits.
        Higher stress from poor sleep, excessive screen time, and poor nutrition.
        """
        stress = 0
        
        # Sleep factor (ideal: 7-9 hours)
        if sleep_hours < 5:
            stress += (5 - sleep_hours) * 8
        elif sleep_hours < 7:
            stress += (7 - sleep_hours) * 5
        elif sleep_hours > 9:
            stress += (sleep_hours - 9) * 3
        
        # Screen time factor (ideal: 4-6 hours)
        if screen_hours > 10:
            stress += (screen_hours - 10) * 5
        elif screen_hours > 8:
            stress += (screen_hours - 8) * 3
        elif screen_hours < 2:
            stress += (2 - screen_hours) * 2
        
        # Work hours factor (ideal: 6-8 hours)
        if work_hours > 10:
            stress += (work_hours - 10) * 4
        elif work_hours < 3:
            stress += (3 - work_hours) * 5
        
        # Social media factor (ideal: 0-1 hour)
        if social_media > 4:
            stress += (social_media - 4) * 8
        elif social_media > 2:
            stress += (social_media - 2) * 5
        
        # Meal quality factor (1-10 scale, lower is worse)
        stress += (10 - meal_quality) * 3
        
        # Average score factor - lower scores can indicate academic pressure
        if average_score < 50:
            stress += (50 - average_score) * 0.5
        elif average_score < 70:
            stress += (70 - average_score) * 0.3
        
        # Procrastination factor - higher procrastination adds stress
        if procrastination >= 7:
            stress += (procrastination - 6) * 5
        elif procrastination >= 4:
            stress += (procrastination - 3) * 2
        
        # Attention span factor - short attention span can cause frustration
        if attention_span <= 3:
            stress += (4 - attention_span) * 4
        elif attention_span <= 5:
            stress += (6 - attention_span) * 2
        
        # Normalize to 0-100
        stress = min(100, max(0, stress))
        return round(stress, 1)
    
    @staticmethod
    def calculate_anxiety_vector(sleep_hours, screen_hours, social_media, meal_quality, average_score, procrastination, attention_span):
        """
        Calculate anxiety vector based on alertness and digital stimulation factors.
        Higher anxiety from insufficient sleep and excessive social media.
        """
        anxiety = 0
        
        # Sleep deprivation creates anxiety
        if sleep_hours < 6:
            anxiety += (6 - sleep_hours) * 12
        elif sleep_hours < 7:
            anxiety += (7 - sleep_hours) * 6
        
        # Social media and screen stimulation increases anxiety
        if social_media > 3:
            anxiety += (social_media - 3) * 10
        elif social_media > 1:
            anxiety += (social_media - 1) * 8
        
        if screen_hours > 10:
            anxiety += (screen_hours - 10) * 4
        elif screen_hours > 8:
            anxiety += (screen_hours - 8) * 3
        
        # Poor nutrition increases anxiety
        anxiety += (10 - meal_quality) * 2
        
        # Average score factor - academic pressure can increase anxiety
        if average_score < 60:
            anxiety += (60 - average_score) * 0.4
        elif average_score < 75:
            anxiety += (75 - average_score) * 0.2
        
        # Procrastination factor - guilt and worry from procrastination
        if procrastination >= 8:
            anxiety += (procrastination - 7) * 6
        elif procrastination >= 5:
            anxiety += (procrastination - 4) * 3
        
        # Attention span factor - difficulty focusing can cause anxiety
        if attention_span <= 3:
            anxiety += (4 - attention_span) * 5
        elif attention_span <= 5:
            anxiety += (6 - attention_span) * 2
        
        # Normalize to 0-100
        anxiety = min(100, max(0, anxiety))
        return round(anxiety, 1)
    
    @staticmethod
    def calculate_productivity_score(work_hours, screen_hours, exercise_hours, sleep_hours, meal_quality, average_score, procrastination, attention_span):
        """
        Calculate productivity score based on work dedication and health factors.
        """
        productivity = 50  # Base score
        
        # Work hours contribution
        if 6 <= work_hours <= 10:
            productivity += (work_hours - 6) * 4
        elif work_hours < 6:
            productivity -= (6 - work_hours) * 5
        elif work_hours > 10:
            productivity -= (work_hours - 10) * 3
        
        # Exercise has positive impact on focus
        if exercise_hours >= 1:
            productivity += min(15, exercise_hours * 10)
        
        # Sleep quality affects productivity
        if 7 <= sleep_hours <= 9:
            productivity += 10
        elif sleep_hours < 7:
            productivity -= (7 - sleep_hours) * 5
        
        # Nutrition affects energy levels
        if meal_quality >= 7:
            productivity += 8
        elif meal_quality < 5:
            productivity -= (5 - meal_quality) * 3
        
        # Excessive screen time can reduce productivity
        if screen_hours > 12:
            productivity -= (screen_hours - 12) * 2
        
        # Average score contributes to productivity assessment
        # Higher academic scores indicate better focus and discipline
        if average_score >= 80:
            productivity += 10
        elif average_score >= 60:
            productivity += 5
        elif average_score < 40:
            productivity -= 10
        elif average_score < 60:
            productivity -= 5
        
        # Procrastination severely impacts productivity
        if procrastination >= 8:
            productivity -= (procrastination - 7) * 8
        elif procrastination >= 5:
            productivity -= (procrastination - 4) * 4
        elif procrastination <= 2:
            productivity += (3 - procrastination) * 5
        
        # Attention span positively affects productivity
        if attention_span >= 8:
            productivity += (attention_span - 7) * 5
        elif attention_span >= 5:
            productivity += (attention_span - 4) * 2
        elif attention_span <= 2:
            productivity -= (3 - attention_span) * 6
        
        # Normalize to 0-100
        productivity = min(100, max(0, productivity))
        return round(productivity, 1)
    
    @staticmethod
    def calculate_overall_wellbeing(stress, anxiety, productivity):
        """
        Calculate overall wellbeing as a weighted average.
        """
        wellbeing = ((100 - stress) * 0.35 + (100 - anxiety) * 0.35 + productivity * 0.3) 
        return round(wellbeing, 1)
    
    @staticmethod
    def get_stress_level(stress_score):
        """Return stress level category."""
        if stress_score < 20:
            return "LOW"
        elif stress_score < 40:
            return "MODERATE"
        elif stress_score < 60:
            return "ELEVATED"
        elif stress_score < 80:
            return "HIGH"
        else:
            return "CRITICAL"
    
    @staticmethod
    def get_anxiety_level(anxiety_score):
        """Return anxiety level category."""
        if anxiety_score < 20:
            return "CALM"
        elif anxiety_score < 40:
            return "MILD"
        elif anxiety_score < 60:
            return "MODERATE"
        elif anxiety_score < 80:
            return "SEVERE"
        else:
            return "ACUTE"
    
    @staticmethod
    def get_productivity_level(productivity_score):
        """Return productivity level category."""
        if productivity_score < 30:
            return "LOW"
        elif productivity_score < 50:
            return "BELOW AVG"
        elif productivity_score < 70:
            return "AVERAGE"
        elif productivity_score < 85:
            return "HIGH"
        else:
            return "PEAK"
    
    @staticmethod
    def generate_recommendations(sleep_hours, screen_hours, work_hours, exercise_hours, 
                                social_media, meal_quality, stress, anxiety, productivity, average_score, procrastination, attention_span):
        """Generate AI recommendations based on analysis."""
        recommendations = []
        
        # Study routine suggestions
        if sleep_hours < 7:
            recommendations.append({
                "category": "Study Routine",
                "title": "Prioritize Rest to Improve Focus",
                "description": f"You're averaging {sleep_hours}h of sleep. A consistent 7-9h sleep schedule supports memory retention and sharper study sessions. Plan your most demanding review topics for the times when you're naturally most alert.",
                "impact": "HIGH",
                "icon": "◉"
            })
        elif sleep_hours > 9:
            recommendations.append({
                "category": "Study Routine",
                "title": "Optimize Your Learning Rhythm",
                "description": "Your current schedule may allow for more structured study time. Use the extra clarity from adequate rest to build a reliable daily study routine with focused sessions and review checkpoints.",
                "impact": "MEDIUM",
                "icon": "◉"
            })

        # Digital discipline recommendations
        if screen_hours > 10:
            recommendations.append({
                "category": "Digital Discipline",
                "title": "Use Screen Time for Focused Study",
                "description": f"You're spending {screen_hours}h on screens daily. Reserve the majority of screen use for active learning, and schedule dedicated digital-free review or note-taking periods to prevent distraction.",
                "impact": "HIGH",
                "icon": "◫"
            })
        
        if social_media > 3:
            recommendations.append({
                "category": "Digital Discipline",
                "title": "Create Social-Free Study Blocks",
                "description": f"You're spending {social_media}h on social media daily. Set strict social-free blocks during study sessions and use short breaks to check socials only after completing a focused task.",
                "impact": "HIGH",
                "icon": "◈"
            })

        # Study planning and workload
        if work_hours > 10:
            recommendations.append({
                "category": "Study Strategy",
                "title": "Shift to High-Quality Study Sessions",
                "description": f"You're studying {work_hours}h daily. Rather than more hours, focus on active recall, practice problems, and spaced repetition to make each study block more effective.",
                "impact": "MEDIUM",
                "icon": "⬡"
            })
        elif work_hours < 3:
            recommendations.append({
                "category": "Study Strategy",
                "title": "Build Focused Study Blocks",
                "description": f"You're studying only {work_hours}h. Increase productivity by planning 3-4 concentrated sessions per day, using techniques like Pomodoro and clear subject goals.",
                "impact": "MEDIUM",
                "icon": "⬡"
            })
        else:
            recommendations.append({
                "category": "Study Strategy",
                "title": "Structure Work into Targeted Study Goals",
                "description": f"Your current study duration of {work_hours}h can be more productive with clearer goals. Break sessions into specific topics, practice questions, and review summaries.",
                "impact": "MEDIUM",
                "icon": "⬡"
            })

        # Cognitive load and focus
        if stress > 70 or anxiety > 75:
            recommendations.append({
                "category": "Study Efficiency",
                "title": "Lower Cognitive Load with Smaller Tasks",
                "description": "Your analysis indicates high mental pressure. Split your study material into smaller, manageable tasks and review one concept at a time to avoid overwhelm.",
                "impact": "CRITICAL",
                "icon": "△"
            })
        
        # Productivity-specific recommendations
        if productivity < 50:
            recommendations.append({
                "category": "Study Efficiency",
                "title": "Refine Your Study Techniques",
                "description": "Your productivity score is below average. Focus on active learning methods like summarizing, self-testing, and teaching concepts out loud to improve retention.",
                "impact": "HIGH",
                "icon": "▲"
            })
        elif productivity > 70:
            recommendations.append({
                "category": "Study Growth",
                "title": "Reinforce Strong Habits",
                "description": "Your productivity is strong. Keep reinforcing this by scheduling review cycles, solving sample questions, and rotating subjects to build long-term mastery.",
                "impact": "POSITIVE",
                "icon": "✓"
            })
        
        # Average score based recommendations
        if average_score < 50:
            recommendations.append({
                "category": "Academic Performance",
                "title": "Address Performance Gaps",
                "description": f"Your average score of {average_score}% indicates potential knowledge gaps. Consider seeking tutoring, forming study groups, or reviewing fundamental concepts to build a stronger foundation.",
                "impact": "HIGH",
                "icon": "★"
            })
        elif average_score >= 85:
            recommendations.append({
                "category": "Academic Performance",
                "title": "Leverage Your Strengths",
                "description": f"Your impressive {average_score}% average shows strong academic performance. Consider mentoring peers or taking on advanced challenges to maximize your potential.",
                "impact": "POSITIVE",
                "icon": "★"
            })
        
        # Procrastination based recommendations
        if procrastination >= 8:
            recommendations.append({
                "category": "Time Management",
                "title": "Break the Procrastination Cycle",
                "description": f"Your procrastination level of {procrastination}/10 is high. Start with the 2-minute rule: if a task takes less than 2 minutes, do it immediately. Use the Pomodoro technique to build momentum.",
                "impact": "CRITICAL",
                "icon": "⏳"
            })
        elif procrastination >= 5:
            recommendations.append({
                "category": "Time Management",
                "title": "Improve Task Initiation",
                "description": f"Procrastination at level {procrastination} suggests difficulty starting tasks. Try setting specific start times, removing distractions, and breaking large tasks into smaller, actionable steps.",
                "impact": "HIGH",
                "icon": "⏳"
            })
        elif procrastination <= 2:
            recommendations.append({
                "category": "Time Management",
                "title": "Maintain Your Focus",
                "description": "Your low procrastination level shows strong self-discipline. Continue using your effective time management strategies and consider helping peers who struggle with task initiation.",
                "impact": "POSITIVE",
                "icon": "⏳"
            })
        
        # Attention span based recommendations
        if attention_span <= 3:
            recommendations.append({
                "category": "Focus Training",
                "title": "Build Extended Focus",
                "description": f"Your attention span of {attention_span}/10 is short. Try mindfulness exercises, the Pomodoro technique (25 min work, 5 min break), and gradually increasing focus duration over time.",
                "impact": "HIGH",
                "icon": "◎"
            })
        elif attention_span >= 8:
            recommendations.append({
                "category": "Focus Training",
                "title": "Leverage Your Strong Focus",
                "description": f"Your attention span of {attention_span}/10 is excellent. Use this strength for deep work sessions on complex tasks that require sustained concentration.",
                "impact": "POSITIVE",
                "icon": "◎"
            })

        return recommendations[:6]  # Return top 6 recommendations
    
    @staticmethod
    def generate_chart_data(sleep_hours, screen_hours, work_hours, exercise_hours, 
                           social_media, meal_quality, stress, anxiety, productivity, average_score, procrastination, attention_span):
        """Generate data for charts."""
        return {
            "radar": {
                "labels": ["Sleep Quality", "Screen Balance", "Exercise", "Nutrition", "Social Balance", "Work Focus", "Academic Score", "Focus Discipline", "Attention Span"],
                "datasets": [{
                    "label": "Your Profile",
                    "data": [
                        min(100, (sleep_hours / 9) * 100),  # Sleep
                        max(0, 100 - (screen_hours / 16) * 100),  # Screen (inverse)
                        min(100, (exercise_hours / 4) * 100),  # Exercise
                        meal_quality * 10,  # Nutrition
                        max(0, 100 - (social_media / 8) * 100),  # Social (inverse)
                        min(100, (work_hours / 10) * 100),  # Work
                        average_score,  # Academic Score
                        max(0, 100 - (procrastination - 1) * 11.1),  # Focus Discipline (inverse of procrastination)
                        attention_span * 10  # Attention Span
                    ],
                    "borderColor": "#00ff88",
                    "backgroundColor": "rgba(0, 255, 136, 0.1)",
                    "borderWidth": 2
                }]
            },
            "polar": {
                "labels": ["Sleep", "Screen Time", "Work Hours", "Exercise", "Social Media", "Meal Quality"],
                "datasets": [{
                    "label": "Input Distribution",
                    "data": [sleep_hours, screen_hours, work_hours, exercise_hours, social_media, meal_quality],
                    "borderColor": "#ff00ff",
                    "backgroundColor": "rgba(255, 0, 255, 0.1)",
                    "borderWidth": 2
                }]
            },
            "bar": {
                "labels": ["Sleep\nDeprivation", "Screen\nOveruse", "Work\nOverload", "Poor\nNutrition", "Social\nExcess"],
                "datasets": [
                    {
                        "label": "Stress Impact",
                        "data": [
                            max(0, 10 - sleep_hours) * 8,
                            max(0, screen_hours - 6) * 4,
                            max(0, work_hours - 8) * 4,
                            (10 - meal_quality) * 3,
                            max(0, social_media - 1) * 8
                        ],
                        "backgroundColor": "#ff4466"
                    },
                    {
                        "label": "Anxiety Impact",
                        "data": [
                            max(0, 7 - sleep_hours) * 10,
                            max(0, screen_hours - 8) * 3,
                            0,
                            (10 - meal_quality) * 2,
                            max(0, social_media - 2) * 10
                        ],
                        "backgroundColor": "#ff88ff"
                    }
                ]
            },
            "line": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "datasets": [
                    {
                        "label": "Stress Trend",
                        "data": [stress * 0.9, stress * 0.95, stress, stress * 1.05, stress * 0.98, stress * 0.88, stress * 0.92],
                        "borderColor": "#ff6644",
                        "tension": 0.3,
                        "fill": False
                    },
                    {
                        "label": "Anxiety Trend",
                        "data": [anxiety * 0.88, anxiety * 0.93, anxiety * 1.02, anxiety, anxiety * 0.97, anxiety * 0.85, anxiety * 0.90],
                        "borderColor": "#ff44ff",
                        "tension": 0.3,
                        "fill": False
                    },
                    {
                        "label": "Productivity Trend",
                        "data": [productivity * 0.92, productivity * 0.95, productivity, productivity * 1.03, productivity * 0.98, productivity * 0.90, productivity * 0.94],
                        "borderColor": "#44ff88",
                        "tension": 0.3,
                        "fill": False
                    }
                ]
            }
        }
    
    @staticmethod
    def get_dataset_stats():
        """Generate statistics from the loaded dataset."""
        if dataset_df is None:
            return None
        
        stats = {
            "total_records": len(dataset_df),
            "age_range": {
                "min": int(dataset_df['Age'].min()),
                "max": int(dataset_df['Age'].max()),
                "mean": float(dataset_df['Age'].mean()),
                "median": float(dataset_df['Age'].median())
            },
            "daily_phone_hours": {
                "min": float(dataset_df['Daily_Phone_Hours'].min()),
                "max": float(dataset_df['Daily_Phone_Hours'].max()),
                "mean": float(dataset_df['Daily_Phone_Hours'].mean()),
                "median": float(dataset_df['Daily_Phone_Hours'].median())
            },
            "social_media_hours": {
                "min": float(dataset_df['Social_Media_Hours'].min()),
                "max": float(dataset_df['Social_Media_Hours'].max()),
                "mean": float(dataset_df['Social_Media_Hours'].mean()),
                "median": float(dataset_df['Social_Media_Hours'].median())
            },
            "sleep_hours": {
                "min": float(dataset_df['Sleep_Hours'].min()),
                "max": float(dataset_df['Sleep_Hours'].max()),
                "mean": float(dataset_df['Sleep_Hours'].mean()),
                "median": float(dataset_df['Sleep_Hours'].median())
            },
            "stress_level": {
                "min": int(dataset_df['Stress_Level'].min()),
                "max": int(dataset_df['Stress_Level'].max()),
                "mean": float(dataset_df['Stress_Level'].mean()),
                "median": float(dataset_df['Stress_Level'].median())
            },
            "work_productivity_score": {
                "min": int(dataset_df['Work_Productivity_Score'].min()),
                "max": int(dataset_df['Work_Productivity_Score'].max()),
                "mean": float(dataset_df['Work_Productivity_Score'].mean()),
                "median": float(dataset_df['Work_Productivity_Score'].median())
            },
            "occupations": dataset_df['Occupation'].value_counts().to_dict(),
            "device_types": dataset_df['Device_Type'].value_counts().to_dict(),
            "genders": dataset_df['Gender'].value_counts().to_dict()
        }
        return stats
    
    @staticmethod
    def get_similar_users(phone_hours, social_hours, sleep_hours, stress_level, productivity, age_min=None, age_max=None):
        """Find similar users from dataset based on current profile."""
        if dataset_df is None or len(dataset_df) == 0:
            return []
        
        # Calculate similarity score using Euclidean distance
        df_copy = dataset_df.copy()
        
        # Filter by age range if provided
        if age_min is not None and age_max is not None:
            df_copy = df_copy[(df_copy['Age'] >= age_min) & (df_copy['Age'] <= age_max)]
        
        if len(df_copy) == 0:
            return []
        
        # Normalize metrics for comparison
        df_copy['similarity'] = np.sqrt(
            ((df_copy['Daily_Phone_Hours'] - phone_hours) / (dataset_df['Daily_Phone_Hours'].std() + 1)) ** 2 +
            ((df_copy['Social_Media_Hours'] - social_hours) / (dataset_df['Social_Media_Hours'].std() + 1)) ** 2 +
            ((df_copy['Sleep_Hours'] - sleep_hours) / (dataset_df['Sleep_Hours'].std() + 1)) ** 2 +
            ((df_copy['Stress_Level'] - stress_level) / (dataset_df['Stress_Level'].std() + 1)) ** 2 +
            ((df_copy['Work_Productivity_Score'] - (productivity / 10)) / (dataset_df['Work_Productivity_Score'].std() + 1)) ** 2
        )
        
        # Get top 5 similar users
        similar = df_copy.nsmallest(6, 'similarity')[1:6]  # Exclude exact match
        
        result = []
        for idx, row in similar.iterrows():
            result.append({
                "user_id": row['User_ID'],
                "age": int(row['Age']),
                "occupation": row['Occupation'],
                "device": row['Device_Type'],
                "daily_phone_hours": float(row['Daily_Phone_Hours']),
                "social_media_hours": float(row['Social_Media_Hours']),
                "sleep_hours": float(row['Sleep_Hours']),
                "stress_level": int(row['Stress_Level']),
                "productivity_score": int(row['Work_Productivity_Score']),
                "similarity_score": float(row['similarity'])
            })
        
        return result
    
    @staticmethod
    def get_percentile(metric_name, value):
        """Calculate user's percentile rank for a given metric."""
        if dataset_df is None or metric_name not in dataset_df.columns:
            return None
        
        percentile = (dataset_df[metric_name] < value).sum() / len(dataset_df) * 100
        return round(percentile, 1)
    
    @staticmethod
    def get_wellbeing_level(value):
        """Return wellbeing level category."""
        if value >= 80:
            return "EXCELLENT"
        elif value >= 65:
            return "GOOD"
        elif value >= 50:
            return "FAIR"
        elif value >= 35:
            return "POOR"
        else:
            return "CRITICAL"


def save_report_internal(data):
    """Internal function to save report after analysis."""
    try:
        report = {
            "userId": data.get("userId"),
            "username": data.get("username", "Anonymous"),
            "timestamp": datetime.now().isoformat(),
            "inputParameters": {
                "sleepHours": data.get("sleepHours"),
                "screenHours": data.get("screenHours"),
                "workHours": data.get("workHours"),
                "exerciseHours": data.get("exerciseHours"),
                "socialMedia": data.get("socialMedia"),
                "mealQuality": data.get("mealQuality"),
                "averageScore": data.get("averageScore"),
                "procrastination": data.get("procrastination"),
                "attentionSpan": data.get("attentionSpan"),
                "ageRange": data.get("ageRange")
            },
            "results": {
                "stressIndex": data.get("stressIndex"),
                "stressLevel": data.get("stressLevel"),
                "anxietyIndex": data.get("anxietyIndex"),
                "anxietyLevel": data.get("anxietyLevel"),
                "productivityRate": data.get("productivityRate"),
                "productivityLevel": data.get("productivityLevel"),
                "overallWellbeing": data.get("overallWellbeing"),
                "wellbeingLevel": data.get("wellbeingLevel")
            },
            "recommendations": data.get("recommendations", []),
            "chartData": data.get("chartData", {}),
            "detailedInsights": {
                "percentiles": data.get("percentiles", {}),
                "similarUsers": data.get("similarUsers", [])
            }
        }
        
        reports_data = load_reports()
        reports_data["reports"].insert(0, report)
        save_reports(reports_data)
        print(f"✓ Report saved: {report['userId']} ({report['username']})")
    except Exception as e:
        print(f"Error saving report: {e}")


@app.route('/')
def index():
    """Serve the main HTML file."""
    return app.send_static_file('dbpa.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze digital behavior."""
    try:
        data = request.json
        
        # Get username or default to "User"
        username = data.get('username', 'User').strip() or 'User'
        
        # Extract input values
        sleep_hours = float(data.get('sleepHours', 7))
        screen_hours = float(data.get('screenHours', 6))
        work_hours = float(data.get('workHours', 8))
        exercise_hours = float(data.get('exerciseHours', 1))
        social_media = float(data.get('socialMedia', 2))
        meal_quality = float(data.get('mealQuality', 6))
        average_score = float(data.get('averageScore', 75))
        procrastination = float(data.get('procrastination', 5))
        attention_span = float(data.get('attentionSpan', 6))
        age_range = data.get('ageRange', None)  # e.g., "18-25", "26-35", "36-45", "46-55", "56+"
        
        # Parse age range to get min and max ages
        age_min, age_max = None, None
        if age_range:
            if age_range == "56+":
                age_min, age_max = 56, 100
            elif "-" in age_range:
                parts = age_range.split("-")
                age_min, age_max = int(parts[0]), int(parts[1])
        
        # Calculate scores
        stress = DBPAAnalysisEngine.calculate_stress_index(
            sleep_hours, screen_hours, work_hours, social_media, meal_quality, average_score, procrastination, attention_span
        )
        anxiety = DBPAAnalysisEngine.calculate_anxiety_vector(
            sleep_hours, screen_hours, social_media, meal_quality, average_score, procrastination, attention_span
        )
        productivity = DBPAAnalysisEngine.calculate_productivity_score(
            work_hours, screen_hours, exercise_hours, sleep_hours, meal_quality, average_score, procrastination, attention_span
        )
        overall = DBPAAnalysisEngine.calculate_overall_wellbeing(stress, anxiety, productivity)
        
        # Get level descriptions
        stress_level = DBPAAnalysisEngine.get_stress_level(stress)
        anxiety_level = DBPAAnalysisEngine.get_anxiety_level(anxiety)
        productivity_level = DBPAAnalysisEngine.get_productivity_level(productivity)
        
        # Generate recommendations
        recommendations = DBPAAnalysisEngine.generate_recommendations(
            sleep_hours, screen_hours, work_hours, exercise_hours, 
            social_media, meal_quality, stress, anxiety, productivity, average_score, procrastination, attention_span
        )
        
        # Generate chart data
        chart_data = DBPAAnalysisEngine.generate_chart_data(
            sleep_hours, screen_hours, work_hours, exercise_hours, 
            social_media, meal_quality, stress, anxiety, productivity, average_score, procrastination, attention_span
        )
        
        # Generate unique user ID for this analysis
        user_id = str(uuid.uuid4())[:8].upper()
        
        # Get percentiles
        percentiles = {
            "stress": DBPAAnalysisEngine.get_percentile("Stress_Level", stress),
            "productivity": DBPAAnalysisEngine.get_percentile("Work_Productivity_Score", productivity / 10),
            "sleep": DBPAAnalysisEngine.get_percentile("Sleep_Hours", sleep_hours),
            "phone_usage": DBPAAnalysisEngine.get_percentile("Daily_Phone_Hours", screen_hours),
            "average_score": average_score
        }
        
        # Get similar users
        similar_users = DBPAAnalysisEngine.get_similar_users(
            screen_hours, social_media, sleep_hours, stress, productivity, age_min, age_max
        )
        
        # Auto-save report
        report_data = {
            "userId": user_id,
            "username": username,
            "sleepHours": sleep_hours,
            "screenHours": screen_hours,
            "workHours": work_hours,
            "exerciseHours": exercise_hours,
            "socialMedia": social_media,
            "mealQuality": meal_quality,
            "averageScore": average_score,
            "procrastination": procrastination,
            "attentionSpan": attention_span,
            "ageRange": age_range or '',
            "stressIndex": stress,
            "stressLevel": stress_level,
            "anxietyIndex": anxiety,
            "anxietyLevel": anxiety_level,
            "productivityRate": productivity,
            "productivityLevel": productivity_level,
            "overallWellbeing": overall,
            "wellbeingLevel": DBPAAnalysisEngine.get_wellbeing_level(overall),
            "recommendations": recommendations,
            "chartData": chart_data,
            "percentiles": percentiles,
            "similarUsers": similar_users
        }
        
        # Save the report
        save_report_internal(report_data)
        
        return jsonify({
            "success": True,
            "userId": user_id,
            "scores": {
                "stress": stress,
                "stressLevel": stress_level,
                "anxiety": anxiety,
                "anxietyLevel": anxiety_level,
                "productivity": productivity,
                "productivityLevel": productivity_level,
                "overall": overall
            },
            "recommendations": recommendations,
            "chartData": chart_data,
            "dataset": {
                "similarUsers": similar_users,
                "percentiles": percentiles
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/dataset/stats', methods=['GET'])
def dataset_stats():
    """Get statistics from the smartphone usage dataset."""
    try:
        stats = DBPAAnalysisEngine.get_dataset_stats()
        if stats is None:
            return jsonify({
                "success": False,
                "error": "Dataset not available"
            }), 404
        
        return jsonify({
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/dataset/insights', methods=['POST'])
def dataset_insights():
    """Get insights based on comparison with dataset."""
    try:
        data = request.json
        
        screen_hours = float(data.get('screenHours', 6))
        social_media = float(data.get('socialMedia', 2))
        sleep_hours = float(data.get('sleepHours', 7))
        stress = float(data.get('stress', 50))
        productivity = float(data.get('productivity', 50))
        
        if dataset_df is None:
            return jsonify({
                "success": False,
                "error": "Dataset not available"
            }), 404
        
        # Get comparisons with dataset averages
        avg_phone = float(dataset_df['Daily_Phone_Hours'].mean())
        avg_social = float(dataset_df['Social_Media_Hours'].mean())
        avg_sleep = float(dataset_df['Sleep_Hours'].mean())
        avg_stress = float(dataset_df['Stress_Level'].mean())
        avg_productivity = float(dataset_df['Work_Productivity_Score'].mean())
        
        insights = {
            "comparisons": {
                "phone_usage": {
                    "user_value": screen_hours,
                    "dataset_average": avg_phone,
                    "difference": screen_hours - avg_phone,
                    "status": "above" if screen_hours > avg_phone else "below",
                    "insight": f"You use your phone {abs(screen_hours - avg_phone):.1f}h {'more' if screen_hours > avg_phone else 'less'} than the dataset average"
                },
                "social_media": {
                    "user_value": social_media,
                    "dataset_average": avg_social,
                    "difference": social_media - avg_social,
                    "status": "above" if social_media > avg_social else "below",
                    "insight": f"Your social media usage is {abs(social_media - avg_social):.1f}h {'more' if social_media > avg_social else 'less'} than average"
                },
                "sleep": {
                    "user_value": sleep_hours,
                    "dataset_average": avg_sleep,
                    "difference": sleep_hours - avg_sleep,
                    "status": "above" if sleep_hours > avg_sleep else "below",
                    "insight": f"You sleep {abs(sleep_hours - avg_sleep):.1f}h {'more' if sleep_hours > avg_sleep else 'less'} than the average user"
                }
            },
            "similar_users": DBPAAnalysisEngine.get_similar_users(screen_hours, social_media, sleep_hours, stress, productivity),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "data": insights
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400



@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    dataset_status = "loaded" if dataset_df is not None else "not_found"
    return jsonify({
        "status": "healthy",
        "service": "DBPA Backend",
        "version": "1.0.0",
        "dataset": {
            "status": dataset_status,
            "records": len(dataset_df) if dataset_df is not None else 0
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/reports/save', methods=['POST'])
def save_report():
    """Save a new analysis report."""
    try:
        data = request.json
        
        # Generate unique user ID
        user_id = data.get('userId') or str(uuid.uuid4())[:8].upper()
        
        # Create report entry
        report = {
            "userId": user_id,
            "timestamp": datetime.now().isoformat(),
            "inputParameters": {
                "sleepHours": float(data.get('sleepHours', 7)),
                "screenHours": float(data.get('screenHours', 6)),
                "workHours": float(data.get('workHours', 8)),
                "exerciseHours": float(data.get('exerciseHours', 1)),
                "socialMedia": float(data.get('socialMedia', 2)),
                "mealQuality": float(data.get('mealQuality', 6)),
                "averageScore": float(data.get('averageScore', 75)),
                "procrastination": float(data.get('procrastination', 5)),
                "attentionSpan": float(data.get('attentionSpan', 6)),
                "ageRange": data.get('ageRange', '')
            },
            "results": {
                "stressIndex": float(data.get('stressIndex', 0)),
                "stressLevel": data.get('stressLevel', 'UNKNOWN'),
                "anxietyIndex": float(data.get('anxietyIndex', 0)),
                "anxietyLevel": data.get('anxietyLevel', 'UNKNOWN'),
                "productivityRate": float(data.get('productivityRate', 0)),
                "productivityLevel": data.get('productivityLevel', 'UNKNOWN'),
                "overallWellbeing": float(data.get('overallWellbeing', 0)),
                "wellbeingLevel": data.get('wellbeingLevel', 'UNKNOWN')
            },
            "recommendations": data.get('recommendations', []),
            "chartData": data.get('chartData', {}),
            "detailedInsights": {
                "percentiles": data.get('percentiles', {}),
                "similarUsers": data.get('similarUsers', [])
            }
        }
        
        # Load existing reports
        reports_data = load_reports()
        
        # Add new report to the beginning
        reports_data["reports"].insert(0, report)
        
        # Save reports
        if save_reports(reports_data):
            return jsonify({
                "success": True,
                "message": "Report saved successfully",
                "userId": user_id,
                "timestamp": report["timestamp"]
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save report"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/reports/history', methods=['GET'])
def get_history():
    """Get all reports history."""
    try:
        reports_data = load_reports()
        reports = reports_data.get("reports", [])
        
        # Return full report data for complete insights
        return jsonify({
            "success": True,
            "history": reports,
            "total": len(reports)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/reports/<user_id>', methods=['GET'])
def get_report(user_id):
    """Get detailed report for a specific user."""
    try:
        reports_data = load_reports()
        reports = reports_data.get("reports", [])
        
        # Find report by user ID
        for report in reports:
            if report.get("userId") == user_id:
                return jsonify({
                    "success": True,
                    "report": report
                })
        
        return jsonify({
            "success": False,
            "error": "Report not found"
        }), 404
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/reports/export', methods=['GET'])
def export_reports_csv():
    """Export all reports to CSV."""
    try:
        reports_data = load_reports()
        reports = reports_data.get("reports", [])
        
        if not reports:
            return jsonify({
                "success": False,
                "error": "No reports to export"
            }), 404
        
        # Create CSV data
        csv_data = []
        for report in reports:
            row = {
                "User ID": report.get("userId"),
                "Timestamp": report.get("timestamp"),
                "Sleep Hours": report.get("inputParameters", {}).get("sleepHours"),
                "Screen Hours": report.get("inputParameters", {}).get("screenHours"),
                "Work Hours": report.get("inputParameters", {}).get("workHours"),
                "Exercise Hours": report.get("inputParameters", {}).get("exerciseHours"),
                "Social Media Hours": report.get("inputParameters", {}).get("socialMedia"),
                "Meal Quality": report.get("inputParameters", {}).get("mealQuality"),
                "Average Score": report.get("inputParameters", {}).get("averageScore"),
                "Procrastination Level": report.get("inputParameters", {}).get("procrastination"),
                "Attention Span": report.get("inputParameters", {}).get("attentionSpan"),
                "Stress Index": report.get("results", {}).get("stressIndex"),
                "Stress Level": report.get("results", {}).get("stressLevel"),
                "Anxiety Index": report.get("results", {}).get("anxietyIndex"),
                "Anxiety Level": report.get("results", {}).get("anxietyLevel"),
                "Productivity Rate": report.get("results", {}).get("productivityRate"),
                "Productivity Level": report.get("results", {}).get("productivityLevel"),
                "Overall Wellbeing": report.get("results", {}).get("overallWellbeing"),
                "Wellbeing Level": report.get("results", {}).get("wellbeingLevel")
            }
            csv_data.append(row)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(csv_data)
        export_path = os.path.join(REPORTS_DIR, f'reports_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(export_path, index=False)
        
        return send_file(
            export_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'dbpa_reports_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/reports/clear', methods=['DELETE'])
def clear_history():
    """Clear all reports history."""
    try:
        reports_data = {"reports": []}
        if save_reports(reports_data):
            return jsonify({
                "success": True,
                "message": "History cleared successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to clear history"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400



if __name__ == '__main__':
    app.run(debug=True, port=5000)
