"""
A/B Testing Metrics Module

Calculates quality scores for gap-filled text:
- Semantic score: Text coherence and completeness
- Domain relevance: Car-specific vocabulary
- Grammar score: Polish case correctness
- Overall score: Weighted combination
"""

import re
from typing import Dict, List, Tuple


class GapFillMetrics:
    """
    Calculates quality metrics for LLM gap-filling in Polish car advertisements.
    """

    # Car domain vocabulary (Polish terms)
    CAR_VOCABULARY = {
        # Colors
        'colors': ['biały', 'czarny', 'srebrny', 'szary', 'czerwony', 'niebieski', 'zielony', 
                   'żółty', 'brązowy', 'bordowy', 'kremowy', 'beżowy', 'metaliczny'],
        
        # Conditions
        'conditions': ['zadbany', 'doskonały', 'bardzo dobry', 'dobry', 'zadowalający', 
                      'porządny', 'słaby', 'zły', 'nowy', 'stary', 'piękny', 'elegancki'],
        
        # Engine types
        'engines': ['benzynowy', 'dieselowy', 'hybrydowy', 'elektryczny', 'lpg', 'cng',
                   'benzynowo-gazowy', 'benzyna', 'diesel', 'paliwo'],
        
        # Fuel types
        'fuel_types': ['benzyna', 'diesel', 'gaz', 'hybryda', 'elektryczny', 'lpg'],
        
        # Transmissions
        'transmissions': ['manualna', 'automatyczna', 'semi-automatyczna', 'cvt', 'powershift'],
        
        # Body types
        'body_types': ['sedan', 'kombi', 'suv', 'crossover', 'coupe', 'cabrio', 'hatchback', 'van', 'mpv'],
        
        # Drive types
        'drive_types': ['przedni', 'tylny', 'pełny', 'stały', 'awd', 'fwd', 'rwd'],
        
        # Features
        'features': ['klimatyzacja', 'nawigacja', 'podgrzewane', 'elektrycze', 'asystent',
                    'czujnik', 'hamulce', 'abs', 'esp', 'airbag', 'airbagi', 'tempomat',
                    'cruise control', 'kamera cofania', 'czujniki parkowania']
    }

    # Polish grammar patterns for case detection
    CASE_ENDINGS = {
        'nominative': ['y', 'i'],  # base form (biały, srebrny)
        'accusative': ['y', 'i'],  # direct object (like nominative for adjectives)
        'genitive': ['ego', 'ego'],  # (białego, srebrnego)
        'dative': ['emu', 'emu'],  # (białemu, srebrnemu)
        'instrumental': ['ym', 'ym'],  # (białym, srebrnym)
        'locative': ['ym', 'ym'],  # (białym, srebrnymi)
    }

    @staticmethod
    def calculate_semantic_score(original_gap_context: str, filled_word: str) -> float:
        """
        Calculate semantic correctness of filled word.
        Uses simple heuristics: word length, consonant patterns, common prefixes.
        
        Args:
            original_gap_context: Text around the gap for context
            filled_word: The word that was filled in
            
        Returns:
            Score 0-1, where 1 is perfect
        """
        score = 0.0
        
        # Check 1: Word length reasonable for Polish (2-20 chars)
        if 2 <= len(filled_word) <= 20:
            score += 0.2
        
        # Check 2: Has vowels (not all consonants)
        vowels = set('aeiouyąęóuiąęó')
        if any(c.lower() in vowels for c in filled_word):
            score += 0.2
        
        # Check 3: Common Polish patterns
        common_patterns = ['ski', 'owy', 'ny', 'owy', 'owy', 'owy', 'owy']
        if any(filled_word.lower().endswith(p) for p in common_patterns):
            score += 0.15
        
        # Check 4: Starts with lowercase (proper case usage)
        if filled_word and filled_word[0].islower():
            score += 0.15
        
        # Check 5: No obvious errors (repeated chars, numbers only)
        if not re.match(r'^\d+$', filled_word) and len(set(filled_word)) > 1:
            score += 0.3
        
        return min(score, 1.0)

    @staticmethod
    def calculate_domain_relevance_score(filled_word: str, context: str = '') -> float:
        """
        Calculate domain relevance: is this a car-related word?
        
        Args:
            filled_word: The word to evaluate
            context: Surrounding text for better context
            
        Returns:
            Score 0-1, where 1 is perfect domain match
        """
        filled_lower = filled_word.lower().strip()
        score = 0.3  # Base score for valid Polish word
        
        # Check if word matches known car vocabulary
        for category, words in GapFillMetrics.CAR_VOCABULARY.items():
            if filled_lower in [w.lower() for w in words]:
                score = 0.9  # Strong domain match
                break
        
        # Check for partial matches (e.g., "biały" matches "biały" in vocabulary)
        for category, words in GapFillMetrics.CAR_VOCABULARY.items():
            for vocab_word in words:
                if filled_lower in vocab_word.lower() or vocab_word.lower() in filled_lower:
                    score = max(score, 0.7)
                    break
        
        # Boost if context contains car-related keywords
        context_lower = context.lower()
        car_keywords = ['samochód', 'auto', 'pojazd', 'silnik', 'lakier', 'przebieg', 'rocznik']
        if any(keyword in context_lower for keyword in car_keywords):
            score = min(score + 0.1, 1.0)
        
        return min(score, 1.0)

    @staticmethod
    def calculate_grammar_score(filled_word: str, context: str, preposition: str = '') -> float:
        """
        Calculate Polish grammar correctness, particularly case agreement.
        
        Args:
            filled_word: The word to evaluate
            context: Surrounding text
            preposition: Preposition before gap (if any) - helps detect required case
            
        Returns:
            Score 0-1, where 1 is grammatically correct
        """
        score = 0.5  # Base score
        
        # Detect required case based on preposition
        case_map = {
            'z': 'instrumental',     # with
            'ze': 'instrumental',
            'w': 'locative',         # in
            'we': 'locative',
            'na': 'locative',
            'o': 'locative',
            'od': 'genitive',        # from
            'do': 'genitive',
            'dla': 'genitive',
            'u': 'genitive',
        }
        
        preposition_lower = preposition.lower().strip()
        required_case = case_map.get(preposition_lower, 'nominative')
        
        # Polish adjective case endings (simplified)
        case_endings_map = {
            'nominative': ['y', 'i', 'owy', 'owy', 'ny'],  # biały, srebrny
            'accusative': ['y', 'i', 'owy', 'ny'],  # Similar to nominative for adjectives
            'genitive': ['ego', 'ogo'],  # białego, srebrnego
            'dative': ['emu', 'emu'],  # białemu, srebrnemu
            'instrumental': ['ym', 'ymi'],  # białym, srebrnymi
            'locative': ['ym', 'ymi'],  # białym, srebrnymi
        }
        
        # Check if word ending matches required case
        word_lower = filled_word.lower()
        if required_case in case_endings_map:
            for ending in case_endings_map[required_case]:
                if word_lower.endswith(ending):
                    score = 0.85
                    break
        
        # Boost if in nominative and no preposition found
        if not preposition_lower and (word_lower.endswith('y') or word_lower.endswith('i') or word_lower.endswith('owy')):
            score = 0.8
        
        # Additional checks
        # If word contains Polish characters, it's likely well-formed
        polish_chars = set('ąćęłńóśźż')
        if any(c in word_lower for c in polish_chars):
            score = min(score + 0.1, 1.0)
        
        return min(score, 1.0)

    @staticmethod
    def calculate_overall_score(
        semantic: float,
        domain_relevance: float,
        grammar: float,
        weights: Dict[str, float] = None
    ) -> float:
        """
        Combine individual metrics into overall score.
        
        Args:
            semantic: Semantic score (0-1)
            domain_relevance: Domain relevance score (0-1)
            grammar: Grammar score (0-1)
            weights: Weights for each component (default: equal)
            
        Returns:
            Overall score 0-1
        """
        if weights is None:
            weights = {
                'semantic': 0.35,
                'domain_relevance': 0.40,
                'grammar': 0.25
            }
        
        overall = (
            semantic * weights['semantic'] +
            domain_relevance * weights['domain_relevance'] +
            grammar * weights['grammar']
        )
        
        return min(overall, 1.0)

    @staticmethod
    def evaluate_gap_fill(
        gap_index: int,
        filled_word: str,
        context: str = '',
        preposition: str = ''
    ) -> Dict:
        """
        Complete evaluation of a single gap fill.
        
        Args:
            gap_index: Gap number (for reference)
            filled_word: The word filled by LLM
            context: Text around the gap
            preposition: Preposition before gap (if any)
            
        Returns:
            Dict with all metric scores and recommendation
        """
        semantic = GapFillMetrics.calculate_semantic_score(context, filled_word)
        domain = GapFillMetrics.calculate_domain_relevance_score(filled_word, context)
        grammar = GapFillMetrics.calculate_grammar_score(filled_word, context, preposition)
        overall = GapFillMetrics.calculate_overall_score(semantic, domain, grammar)
        
        return {
            'gap_index': gap_index,
            'filled_word': filled_word,
            'semantic_score': round(semantic, 3),
            'domain_relevance_score': round(domain, 3),
            'grammar_score': round(grammar, 3),
            'overall_score': round(overall, 3),
            'quality_level': GapFillMetrics._classify_quality(overall)
        }

    @staticmethod
    def _classify_quality(score: float) -> str:
        """Classify overall score into quality level."""
        if score >= 0.85:
            return 'excellent'
        elif score >= 0.70:
            return 'good'
        elif score >= 0.55:
            return 'acceptable'
        elif score >= 0.40:
            return 'poor'
        else:
            return 'unacceptable'

    @staticmethod
    def evaluate_multiple_fills(fills: List[Dict]) -> Dict:
        """
        Evaluate multiple gap fills from a single run.
        
        Args:
            fills: List of dicts with 'index', 'word', 'context', optional 'preposition'
            
        Returns:
            Dict with per-gap scores and run-level statistics
        """
        evaluations = []
        for fill in fills:
            evaluation = GapFillMetrics.evaluate_gap_fill(
                gap_index=fill.get('index'),
                filled_word=fill.get('word'),
                context=fill.get('context', ''),
                preposition=fill.get('preposition', '')
            )
            evaluations.append(evaluation)
        
        # Calculate aggregate statistics
        if evaluations:
            avg_semantic = sum(e['semantic_score'] for e in evaluations) / len(evaluations)
            avg_domain = sum(e['domain_relevance_score'] for e in evaluations) / len(evaluations)
            avg_grammar = sum(e['grammar_score'] for e in evaluations) / len(evaluations)
            avg_overall = sum(e['overall_score'] for e in evaluations) / len(evaluations)
        else:
            avg_semantic = avg_domain = avg_grammar = avg_overall = 0.0
        
        return {
            'gap_evaluations': evaluations,
            'average_semantic': round(avg_semantic, 3),
            'average_domain_relevance': round(avg_domain, 3),
            'average_grammar': round(avg_grammar, 3),
            'average_overall': round(avg_overall, 3),
            'total_gaps': len(evaluations),
            'quality_breakdown': {
                'excellent': sum(1 for e in evaluations if e['quality_level'] == 'excellent'),
                'good': sum(1 for e in evaluations if e['quality_level'] == 'good'),
                'acceptable': sum(1 for e in evaluations if e['quality_level'] == 'acceptable'),
                'poor': sum(1 for e in evaluations if e['quality_level'] == 'poor'),
                'unacceptable': sum(1 for e in evaluations if e['quality_level'] == 'unacceptable'),
            }
        }
