class Scorer:
    def calculate_score(self, lead_data, analysis_data):
        # 1. Technical/Bad Website Score (0-100, higher is worse website)
        tech_faults = 0
        if analysis_data:
            if not analysis_data['https']: tech_faults += 30
            if not analysis_data['mobile_responsive']: tech_faults += 30
            if analysis_data['load_time'] > 4: tech_faults += 20
            if not analysis_data['has_cta']: tech_faults += 20
        else:
            # If we couldn't analyze (e.g. timeout), it's probably a bad site
            tech_faults = 100
            
        bad_website_score = min(tech_faults, 100)
        
        # 2. Builder Bonus (0-100)
        builder_bonus = 0
        if analysis_data:
            builder = analysis_data['builder']
            if analysis_data['is_ai_builder'] or builder in ['GoDaddy', 'Hostinger', 'Wix', 'Weebly']:
                builder_bonus = 100
            elif builder == 'WordPress':
                builder_bonus = 40
            elif builder == 'Shopify':
                builder_bonus = 0 # Hard to move
            elif builder in ['React', 'Next.js']:
                builder_bonus = 0 # Already custom
        
        # 3. No Email Bonus (0-100)
        email_bonus = 0
        if analysis_data:
            if not analysis_data['emails']:
                email_bonus = 100
            elif analysis_data['email_quality'] == 'Generic':
                email_bonus = 50
            else:
                email_bonus = 0
        
        # 4. Review Count Score (0-100)
        # We want small businesses.
        reviews = lead_data.get('reviews', 0)
        review_score = 0
        if reviews < 10:
            review_score = 100
        elif reviews < 50:
            review_score = 70
        elif reviews < 100:
            review_score = 40
        else:
            review_score = 0
            
        # Final Formula
        # (Bad Website Score × 0.4) + (AI Builder Bonus × 0.2) + (No Email Bonus × 0.25) + (Low Review Count × 0.15)
        final_priority = (bad_website_score * 0.4) + (builder_bonus * 0.2) + (email_bonus * 0.25) + (review_score * 0.15)
        
        # Determine Tier
        tier = "Ignore"
        if final_priority >= 80:
            tier = "Tier-1 Gold"
        elif final_priority >= 60:
            tier = "Tier-1"
        elif final_priority >= 40:
            tier = "Tier-2"
            
        return {
            'final_priority': round(final_priority, 1),
            'tier': tier,
            'breakdown': {
                'bad_website_score': bad_website_score,
                'builder_bonus': builder_bonus,
                'email_bonus': email_bonus,
                'review_score': review_score
            }
        }
