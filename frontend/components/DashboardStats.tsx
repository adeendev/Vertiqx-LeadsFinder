import { Users, Mail, Zap, TrendingUp, AlertTriangle, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface DashboardStatsProps {
  leads: any[];
}

export default function DashboardStats({ leads }: DashboardStatsProps) {
  const totalLeads = leads.length;
  const emailsSent = leads.filter(l => l.email_sent).length;
  const avgScore = totalLeads > 0 
    ? Math.round(leads.reduce((acc, l) => acc + l.final_priority, 0) / totalLeads) 
    : 0;
  
  const highPotential = leads.filter(l => l.final_priority >= 70).length;

  const stats = [
    {
      label: 'Total Leads',
      value: totalLeads,
      icon: Users,
      color: 'blue',
      gradient: 'from-blue-500 to-indigo-600',
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      desc: 'Active database',
      trend: '+12%', // Fake trend for UI demo
      trendUp: true
    },
    {
      label: 'Emails Sent',
      value: emailsSent,
      icon: Mail,
      color: 'purple',
      gradient: 'from-purple-500 to-pink-600',
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      desc: `${totalLeads > 0 ? Math.round((emailsSent / totalLeads) * 100) : 0}% outreach rate`,
      trend: '+5%',
      trendUp: true
    },
    {
      label: 'Avg. Score',
      value: avgScore,
      icon: TrendingUp,
      color: 'emerald',
      gradient: 'from-emerald-500 to-teal-600',
      bg: 'bg-emerald-50',
      text: 'text-emerald-600',
      desc: 'Quality index',
      trend: '+2.4',
      trendUp: true
    },
    {
      label: 'High Potential',
      value: highPotential,
      icon: Zap,
      color: 'amber',
      gradient: 'from-amber-500 to-orange-600',
      bg: 'bg-amber-50',
      text: 'text-amber-600',
      desc: 'Score 70+',
      trend: '-1%',
      trendUp: false
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, i) => (
        <div key={i} className="group bg-white p-6 rounded-2xl shadow-[0_2px_10px_-4px_rgba(6,81,237,0.1)] border border-slate-100 hover:border-slate-200 hover:shadow-[0_8px_30px_-12px_rgba(6,81,237,0.2)] transition-all duration-300 relative overflow-hidden">
          {/* Decorative background blur */}
          <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.gradient} opacity-[0.03] group-hover:opacity-[0.08] rounded-bl-full transition-opacity duration-500`}></div>
          
          <div className="relative">
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-2xl ${stat.bg} ${stat.text} shadow-sm group-hover:scale-110 transition-transform duration-300`}>
                <stat.icon size={22} strokeWidth={2.5} />
              </div>
              <div className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full ${stat.trendUp ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                {stat.trendUp ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                {stat.trend}
              </div>
            </div>
            
            <div>
              <h3 className="text-3xl font-extrabold text-slate-900 tracking-tight">{stat.value}</h3>
              <p className="text-sm font-medium text-slate-500 mt-1">{stat.label}</p>
            </div>
            
            <div className="mt-4 pt-3 border-t border-slate-50">
                <p className="text-xs font-semibold text-slate-400">{stat.desc}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
