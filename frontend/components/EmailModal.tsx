import React, { useState, useEffect } from 'react';
import { X, Send, CheckCircle, AlertCircle, Mail, Globe, Lock } from 'lucide-react';
import axios from 'axios';

interface EmailModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead: any;
}

export default function EmailModal({ isOpen, onClose, lead }: EmailModalProps) {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [settings, setSettings] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      axios.get('http://localhost:8000/api/settings')
        .then(res => setSettings(res.data))
        .catch(err => console.error("Failed to load settings", err));
    }
  }, [isOpen]);

  useEffect(() => {
    if (lead && settings) {
      let subj = '';
      let body = '';
      
      const replacePlaceholders = (text: string) => {
          if (!text) return '';
          return text
            .replace(/{business_name}/g, lead.business_name)
            .replace(/{diagnosis}/g, lead.pain_points || 'general improvements');
      };

      // Logic to determine which template to use
      if (!lead.domain) {
          // No Website
          subj = settings.TEMPLATE_NO_WEBSITE_SUBJECT;
          body = settings.TEMPLATE_NO_WEBSITE_BODY;
      } else if (lead.technical_score >= 95) { 
          // Website Down/Not Working (High technical score usually implies analysis failed or very bad)
          subj = settings.TEMPLATE_NOT_WORKING_SUBJECT;
          body = settings.TEMPLATE_NOT_WORKING_BODY;
      } else {
          // Working but with issues
          subj = settings.TEMPLATE_WITH_ISSUES_SUBJECT;
          body = settings.TEMPLATE_WITH_ISSUES_BODY;
      }
      
      // Fallback defaults if settings are missing
      if (!subj) subj = `Partnership Opportunity: ${lead.business_name}`;
      if (!body) body = `Hi Team at ${lead.business_name},\n\nI came across your business and noticed a few opportunities for growth.\n\nBest,\n[Your Name]`;

      setSubject(replacePlaceholders(subj));
      setMessage(replacePlaceholders(body));
    }
  }, [lead, settings]);

  if (!isOpen || !lead) return null;

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      await axios.post('http://localhost:8000/api/send_email', {
        to_email: lead.email,
        subject: subject,
        message: message,
        lead_id: lead.id,
        use_html: true // Convert newlines to BRs or similar in backend if needed, or send HTML here
      });
      
      setStatus({ type: 'success', message: 'Email sent successfully!' });
      setTimeout(() => {
        onClose();
        setStatus(null);
      }, 2000);
    } catch (error: any) {
      console.error(error);
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to send email. Check backend logs.' 
      });
    } finally {
      setLoading(false);
    }
  };

  // Convert text newlines to simple HTML breaks for the preview/sending
  const getHtmlMessage = (text: string) => {
    return text.replace(/\n/g, '<br>');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 flex justify-between items-center text-white">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <Mail size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold">Compose Email</h2>
              <p className="text-blue-100 text-sm">To: {lead.business_name} ({lead.email})</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-full transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto flex-1">
          <form onSubmit={handleSend} className="space-y-4">
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl h-64 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition resize-none font-sans"
                required
              />
            </div>

            {/* Status Message */}
            {status && (
              <div className={`p-4 rounded-xl flex items-center gap-3 ${
                status.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'
              }`}>
                {status.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
                <p className="font-medium">{status.message}</p>
              </div>
            )}

            {/* Footer Actions */}
            <div className="pt-4 border-t border-gray-100 flex justify-between items-center">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Lock size={12} />
                <span>Secure SSL Connection</span>
              </div>
              
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-2.5 text-gray-600 font-medium hover:bg-gray-50 rounded-xl transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition shadow-lg shadow-blue-600/20 flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Send Email
                    </>
                  )}
                </button>
              </div>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
}
