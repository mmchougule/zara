from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class DecisionEngine:
    def __init__(self, config: Dict):
        self.config = config
        self.state_history = []
        self.decision_weights = self._initialize_weights()
        self.learning_rate = config.get('adaptation_parameters', {}).get('learning_rate', 0.2)

    def _initialize_weights(self) -> Dict:
        """Initialize decision weights based on config"""
        return {
            'content_creation': {
                'timing': 0.3,
                'topic_selection': 0.3,
                'style_choice': 0.2,
                'context_relevance': 0.2
            },
            'engagement': {
                'response_priority': 0.4,
                'depth_level': 0.3,
                'style_matching': 0.3
            },
            'trend_analysis': {
                'urgency': 0.4,
                'relevance': 0.3,
                'impact': 0.3
            }
        }

    async def evaluate_action(self, action_type: str, context: Dict) -> Dict:
        """Evaluate whether to take an action and how"""
        scores = await self._calculate_action_scores(action_type, context)
        decision = await self._make_decision(action_type, scores)
        
        # Record decision for learning
        self.state_history.append({
            'timestamp': datetime.now(),
            'action_type': action_type,
            'context': context,
            'scores': scores,
            'decision': decision
        })
        
        return decision

    async def _calculate_action_scores(self, action_type: str, context: Dict) -> Dict:
        """Calculate scores for different aspects of an action"""
        weights = self.decision_weights[action_type]
        scores = {}
        
        if action_type == 'content_creation':
            scores = {
                'timing': self._evaluate_timing(context),
                'topic_selection': self._evaluate_topic(context),
                'style_choice': self._evaluate_style(context),
                'context_relevance': self._evaluate_context(context)
            }
        elif action_type == 'engagement':
            scores = {
                'response_priority': self._evaluate_priority(context),
                'depth_level': self._evaluate_depth(context),
                'style_matching': self._evaluate_style_match(context)
            }
        elif action_type == 'trend_analysis':
            scores = {
                'urgency': self._evaluate_urgency(context),
                'relevance': self._evaluate_relevance(context),
                'impact': self._evaluate_impact(context)
            }
            
        return {k: v * weights[k] for k, v in scores.items()}

    async def _make_decision(self, action_type: str, scores: Dict) -> Dict:
        """Make final decision based on scores"""
        total_score = sum(scores.values())
        threshold = self._get_threshold(action_type)
        
        should_act = total_score >= threshold
        
        return {
            'should_act': should_act,
            'confidence': total_score / len(scores),
            'scores': scores,
            'reasoning': self._generate_reasoning(action_type, scores)
        }

    def _evaluate_timing(self, context: Dict) -> float:
        """Evaluate timing appropriateness"""
        last_action_time = context.get('last_action_time')
        if not last_action_time:
            return 1.0
            
        time_diff = datetime.now() - last_action_time
        optimal_interval = timedelta(hours=24/self.config['behavioral_patterns']['content_creation']['daily_posts'])
        
        return min(time_diff/optimal_interval, 1.0)

    def _evaluate_topic(self, context: Dict) -> float:
        """Evaluate topic relevance"""
        current_trends = context.get('trends', [])
        target_themes = self.config.get('content_themes', {}).get('primary', [])
        
        if not current_trends or not target_themes:
            return 0.5
            
        relevance_score = sum(
            1 for trend in current_trends 
            if any(theme.lower() in trend.lower() for theme in target_themes)
        ) / len(current_trends)
        
        return relevance_score

    def _evaluate_style(self, context: Dict) -> float:
        """Evaluate style appropriateness"""
        current_focus = context.get('current_focus', '')
        style_guidelines = self.config.get('interaction_rules', [])
        
        if not current_focus or not style_guidelines:
            return 0.5
            
        return 0.8  # Default high confidence in style

    def _evaluate_context(self, context: Dict) -> float:
        """Evaluate context relevance"""
        if not context:
            return 0.5
            
        relevant_factors = [
            'trends' in context,
            'recent_discussions' in context,
            'community_focus' in context
        ]
        
        return sum(relevant_factors) / len(relevant_factors)

    def _evaluate_priority(self, context: Dict) -> float:
        """Evaluate response priority"""
        if 'urgency' in context:
            return context['urgency']
        return 0.5

    def _evaluate_depth(self, context: Dict) -> float:
        """Evaluate required depth of response"""
        if 'complexity' in context:
            return context['complexity']
        return 0.7

    def _evaluate_style_match(self, context: Dict) -> float:
        """Evaluate style matching requirements"""
        return 0.8  # Default high confidence in style matching

    def _evaluate_urgency(self, context: Dict) -> float:
        """Evaluate trend analysis urgency"""
        last_analysis = context.get('last_analysis_time')
        if not last_analysis:
            return 1.0
            
        time_diff = datetime.now() - last_analysis
        threshold = timedelta(minutes=30)  # Configurable
        
        return min(time_diff/threshold, 1.0)

    def _evaluate_relevance(self, context: Dict) -> float:
        """Evaluate trend relevance"""
        return 0.8  # Default high relevance

    def _evaluate_impact(self, context: Dict) -> float:
        """Evaluate potential impact"""
        return 0.7  # Default moderate impact

    def _get_threshold(self, action_type: str) -> float:
        """Get decision threshold for action type"""
        thresholds = {
            'content_creation': 0.6,
            'engagement': 0.5,
            'trend_analysis': 0.4
        }
        return thresholds.get(action_type, 0.5)

    def _generate_reasoning(self, action_type: str, scores: Dict) -> str:
        """Generate explanation for decision"""
        reasons = []
        for aspect, score in scores.items():
            if score > 0.7:
                reasons.append(f"Strong {aspect} ({score:.2f})")
            elif score > 0.4:
                reasons.append(f"Moderate {aspect} ({score:.2f})")
            else:
                reasons.append(f"Weak {aspect} ({score:.2f})")
                
        return f"Decision based on: {', '.join(reasons)}"

    async def update_weights(self, feedback: Dict):
        """Update decision weights based on feedback"""
        for action_type, aspects in feedback.items():
            for aspect, performance in aspects.items():
                current_weight = self.decision_weights[action_type][aspect]
                self.decision_weights[action_type][aspect] = (
                    current_weight * (1 - self.learning_rate) +
                    performance * self.learning_rate
                ) 