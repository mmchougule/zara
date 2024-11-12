from typing import Dict

class StrategyManager:
    async def update_content_strategy(self, metrics: Dict):
        """Update content strategy based on engagement"""
        # Analyze what content performs best
        best_formats = self._analyze_format_performance(metrics)
        best_topics = self._analyze_topic_performance(metrics)
        best_times = self._analyze_posting_times(metrics)
        
        # Update generation parameters
        await self.content_generator.update_preferences({
            'preferred_formats': best_formats,
            'preferred_topics': best_topics,
            'optimal_times': best_times
        }) 