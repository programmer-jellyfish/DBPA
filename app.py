from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
    def calculate_stress_index(sleep_hours, screen_hours, work_hours, social_media, meal_quality):
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
        
        # Normalize to 0-100
        stress = min(100, max(0, stress))
        return round(stress, 1)
    
    @staticmethod
    def calculate_anxiety_vector(sleep_hours, screen_hours, social_media, meal_quality):
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
        
        # Normalize to 0-100
        anxiety = min(100, max(0, anxiety))
        return round(anxiety, 1)
    
    @staticmethod
    def calculate_productivity_score(work_hours, screen_hours, exercise_hours, sleep_hours, meal_quality):
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
                                social_media, meal_quality, stress, anxiety, productivity):
        """Generate AI recommendations based on analysis."""
        recommendations = []
        
        # Sleep recommendations
        if sleep_hours < 7:
            recommendations.append({
                "category": "Sleep",
                "title": "Increase Sleep Duration",
                "description": f"You're averaging {sleep_hours}h of sleep. Aim for 7-9 hours to reduce stress and improve cognitive function.",
                "impact": "HIGH",
                "icon": "◉"
            })
        elif sleep_hours > 9:
            recommendations.append({
                "category": "Sleep",
                "title": "Optimize Sleep Duration",
                "description": f"You're sleeping {sleep_hours}h, which may indicate oversleep. Reduce to 7-9 hours for better energy.",
                "impact": "MEDIUM",
                "icon": "◉"
            })
        
        # Screen time recommendations
        if screen_hours > 10:
            recommendations.append({
                "category": "Digital Wellness",
                "title": "Reduce Screen Exposure",
                "description": f"You're on screens for {screen_hours}h daily. This significantly impacts stress. Aim for 6-8 hours.",
                "impact": "HIGH",
                "icon": "◫"
            })
        
        # Social media recommendations
        if social_media > 3:
            recommendations.append({
                "category": "Digital Wellness",
                "title": "Limit Social Media",
                "description": f"You're spending {social_media}h on social platforms daily. Reduce to under 2 hours to lower anxiety.",
                "impact": "HIGH",
                "icon": "◈"
            })
        
        # Exercise recommendations
        if exercise_hours < 0.5:
            recommendations.append({
                "category": "Physical Health",
                "title": "Add Movement",
                "description": "You're not exercising regularly. Even 30 minutes daily exercise can significantly reduce stress and improve mood.",
                "impact": "HIGH",
                "icon": "◎"
            })
        elif exercise_hours < 1:
            recommendations.append({
                "category": "Physical Health",
                "title": "Increase Exercise",
                "description": f"Current activity is {exercise_hours}h. Aim for at least 1 hour daily for optimal mental health.",
                "impact": "MEDIUM",
                "icon": "◎"
            })
        
        # Nutrition recommendations
        if meal_quality < 6:
            recommendations.append({
                "category": "Nutrition",
                "title": "Improve Meal Quality",
                "description": f"Your nutrition score is {meal_quality}/10. Focus on balanced meals to support mental and physical health.",
                "impact": "HIGH",
                "icon": "◇"
            })
        
        # Work/Study recommendations
        if work_hours > 10:
            recommendations.append({
                "category": "Work Balance",
                "title": "Reduce Work Hours",
                "description": f"You're working {work_hours}h daily. Aim for 8 hours to prevent burnout and maintain productivity.",
                "impact": "MEDIUM",
                "icon": "⬡"
            })
        elif work_hours < 3:
            recommendations.append({
                "category": "Work Balance",
                "title": "Increase Productive Time",
                "description": f"You're working only {work_hours}h. Consider increasing focused work sessions for better outcomes.",
                "impact": "MEDIUM",
                "icon": "⬡"
            })
        
        # Stress-specific recommendations
        if stress > 70:
            recommendations.append({
                "category": "Mental Health",
                "title": "High Stress Detected",
                "description": "Your stress levels are elevated. Consider meditation, deep breathing, or consulting a mental health professional.",
                "impact": "CRITICAL",
                "icon": "△"
            })
        
        # Anxiety-specific recommendations
        if anxiety > 75:
            recommendations.append({
                "category": "Mental Health",
                "title": "Anxiety Management",
                "description": "Your anxiety is high. Try mindfulness practices, reduce caffeine intake, and establish digital boundaries.",
                "impact": "CRITICAL",
                "icon": "▲"
            })
        
        # Positive feedback
        if stress < 40 and anxiety < 40 and productivity > 65:
            recommendations.append({
                "category": "Positive",
                "title": "Great Balance!",
                "description": "Your daily habits are well-balanced. Maintain this routine and continue monitoring your metrics.",
                "impact": "POSITIVE",
                "icon": "✓"
            })
        
        return recommendations[:6]  # Return top 6 recommendations
    
    @staticmethod
    def generate_chart_data(sleep_hours, screen_hours, work_hours, exercise_hours, 
                           social_media, meal_quality, stress, anxiety, productivity):
        """Generate data for charts."""
        return {
            "radar": {
                "labels": ["Sleep Quality", "Screen Balance", "Exercise", "Nutrition", "Social Balance", "Work Focus"],
                "datasets": [{
                    "label": "Your Profile",
                    "data": [
                        min(100, (sleep_hours / 9) * 100),  # Sleep
                        max(0, 100 - (screen_hours / 16) * 100),  # Screen (inverse)
                        min(100, (exercise_hours / 4) * 100),  # Exercise
                        meal_quality * 10,  # Nutrition
                        max(0, 100 - (social_media / 8) * 100),  # Social (inverse)
                        min(100, (work_hours / 10) * 100)  # Work
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
    def get_similar_users(phone_hours, social_hours, sleep_hours, stress_level, productivity):
        """Find similar users from dataset based on current profile."""
        if dataset_df is None or len(dataset_df) == 0:
            return []
        
        # Calculate similarity score using Euclidean distance
        df_copy = dataset_df.copy()
        
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


@app.route('/')
def index():
    """Serve the main HTML file."""
    return app.send_static_file('dbpa.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze digital behavior."""
    try:
        data = request.json
        
        # Extract input values
        sleep_hours = float(data.get('sleepHours', 7))
        screen_hours = float(data.get('screenHours', 6))
        work_hours = float(data.get('workHours', 8))
        exercise_hours = float(data.get('exerciseHours', 1))
        social_media = float(data.get('socialMedia', 2))
        meal_quality = float(data.get('mealQuality', 6))
        
        # Calculate scores
        stress = DBPAAnalysisEngine.calculate_stress_index(
            sleep_hours, screen_hours, work_hours, social_media, meal_quality
        )
        anxiety = DBPAAnalysisEngine.calculate_anxiety_vector(
            sleep_hours, screen_hours, social_media, meal_quality
        )
        productivity = DBPAAnalysisEngine.calculate_productivity_score(
            work_hours, screen_hours, exercise_hours, sleep_hours, meal_quality
        )
        overall = DBPAAnalysisEngine.calculate_overall_wellbeing(stress, anxiety, productivity)
        
        # Get level descriptions
        stress_level = DBPAAnalysisEngine.get_stress_level(stress)
        anxiety_level = DBPAAnalysisEngine.get_anxiety_level(anxiety)
        productivity_level = DBPAAnalysisEngine.get_productivity_level(productivity)
        
        # Generate recommendations
        recommendations = DBPAAnalysisEngine.generate_recommendations(
            sleep_hours, screen_hours, work_hours, exercise_hours, 
            social_media, meal_quality, stress, anxiety, productivity
        )
        
        # Generate chart data
        chart_data = DBPAAnalysisEngine.generate_chart_data(
            sleep_hours, screen_hours, work_hours, exercise_hours, 
            social_media, meal_quality, stress, anxiety, productivity
        )
        
        return jsonify({
            "success": True,
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
                "similarUsers": DBPAAnalysisEngine.get_similar_users(
                    screen_hours, social_media, sleep_hours, stress, productivity
                ),
                "percentiles": {
                    "stress": DBPAAnalysisEngine.get_percentile("Stress_Level", stress),
                    "productivity": DBPAAnalysisEngine.get_percentile("Work_Productivity_Score", productivity / 10),
                    "sleep": DBPAAnalysisEngine.get_percentile("Sleep_Hours", sleep_hours),
                    "phone_usage": DBPAAnalysisEngine.get_percentile("Daily_Phone_Hours", screen_hours)
                }
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)