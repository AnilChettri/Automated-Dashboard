import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Users, 
  Package, 
  MessageSquare, 
  TrendingUp, 
  AlertCircle, 
  BrainCircuit, 
  ChevronRight,
  Search,
  Settings,
  Bell,
  ArrowUpRight,
  ArrowDownRight,
  Zap
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  BarChart, Bar, Cell, PieChart, Pie
} from 'recharts';
import { analyticsApi, forecastApi, insightApi, chatApi, mlApi, recommendationApi } from './api';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for Tailwind classes
function cn(...inputs) {
  return twMerge(clsx(inputs));
}

// --- Components ---

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button 
    onClick={onClick}
    className={cn(
      "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group",
      active ? "bg-primary text-white shadow-lg shadow-primary/20" : "text-muted-foreground hover:bg-accent hover:text-foreground"
    )}
  >
    <Icon size={20} className={cn(active ? "text-white" : "group-hover:text-primary")} />
    <span className="font-medium">{label}</span>
  </button>
);

const KpiCard = ({ label, value, trend, trendValue, icon: Icon, color }) => (
  <div className="glass-card p-6 rounded-xl animate-in">
    <div className="flex justify-between items-start mb-4">
      <div className={cn("p-2 rounded-lg", color)}>
        <Icon size={24} className="text-white" />
      </div>
      <div className={cn(
        "flex items-center gap-1 text-sm font-medium",
        trend === 'up' ? "text-emerald-400" : "text-rose-400"
      )}>
        {trend === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        {trendValue}%
      </div>
    </div>
    <div>
      <p className="text-muted-foreground text-sm font-medium mb-1">{label}</p>
      <h3 className="text-2xl font-bold">{value}</h3>
    </div>
  </div>
);

const InsightCard = ({ insight }) => (
  <div className="glass-card p-5 rounded-xl border-l-4 border-l-primary animate-in mb-4">
    <div className="flex items-center gap-2 mb-2">
      <div className={cn(
        "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
        insight.severity === 'critical' ? "bg-rose-500/20 text-rose-400" : 
        insight.severity === 'warning' ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500/20 text-emerald-400"
      )}>
        {insight.severity}
      </div>
      <span className="text-muted-foreground text-xs">{insight.category}</span>
    </div>
    <h4 className="font-bold text-foreground mb-1">{insight.title}</h4>
    <p className="text-muted-foreground text-sm leading-relaxed">{insight.body}</p>
  </div>
);

// --- Main App ---

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [kpis, setKpis] = useState(null);
  const [revenueTrend, setRevenueTrend] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [insights, setInsights] = useState([]);
  const [segments, setSegments] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [chatQuery, setChatQuery] = useState('');
  const [chatResponse, setChatResponse] = useState(null);
  const [isChatLoading, setIsChatLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [kpiRes, trendRes, insightRes, segmentRes, productsRes, forecastRes] = await Promise.all([
        analyticsApi.getKpis(),
        analyticsApi.getRevenueTrend(),
        insightApi.getLatest(),
        analyticsApi.getSegments(),
        analyticsApi.getTopProducts(),
        forecastApi.getRevenueForecast().catch(() => ({ data: { data: [] } }))
      ]);

      setKpis(kpiRes.data);
      setRevenueTrend(trendRes.data.data);
      setInsights(insightRes.data.insights);
      setSegments(segmentRes.data.segments);
      setTopProducts(productsRes.data.data);
      setForecast(forecastRes.data.data);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatQuery.trim()) return;

    setIsChatLoading(true);
    try {
      const res = await chatApi.ask(chatQuery);
      setChatResponse(res.data);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Prepare chart data (combine actual + forecast)
  const chartData = [
    ...revenueTrend.map(d => ({ date: d.date, revenue: d.revenue, type: 'actual' })),
    ...forecast.map(d => ({ date: d.date, revenue: d.predicted, type: 'forecast' }))
  ];

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border p-6 flex flex-col gap-8 hidden lg:flex">
        <div className="flex items-center gap-3 px-2">
          <div className="bg-primary p-1.5 rounded-lg">
            <BrainCircuit size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Intelligence</h1>
        </div>

        <nav className="flex flex-col gap-2 flex-1">
          <SidebarItem 
            icon={LayoutDashboard} 
            label="Dashboard" 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')} 
          />
          <SidebarItem 
            icon={Users} 
            label="Customers" 
            active={activeTab === 'customers'} 
            onClick={() => setActiveTab('customers')} 
          />
          <SidebarItem 
            icon={Package} 
            label="Products" 
            active={activeTab === 'products'} 
            onClick={() => setActiveTab('products')} 
          />
          <SidebarItem 
            icon={MessageSquare} 
            label="AI Chat" 
            active={activeTab === 'chat'} 
            onClick={() => setActiveTab('chat')} 
          />
        </nav>

        <div className="pt-6 border-t border-border">
          <SidebarItem icon={Settings} label="Settings" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header */}
        <header className="h-20 border-b border-border flex items-center justify-between px-8 bg-background/50 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-4 bg-accent/50 px-4 py-2 rounded-full border border-border w-96">
            <Search size={18} className="text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search data, customers, or insights..." 
              className="bg-transparent border-none focus:outline-none text-sm w-full"
            />
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-accent rounded-full transition-colors relative">
              <Bell size={20} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-background"></span>
            </button>
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-purple-600 border-2 border-border flex items-center justify-center font-bold">
              AC
            </div>
          </div>
        </header>

        {/* Viewport */}
        <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
          {activeTab === 'dashboard' && (
            <div className="space-y-8 animate-in">
              <div className="flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-bold mb-1">Business Overview</h2>
                  <p className="text-muted-foreground">Real-time metrics and AI-powered insights for your store.</p>
                </div>
                <div className="flex gap-3">
                   <button className="px-4 py-2 bg-accent text-sm font-medium rounded-lg hover:bg-accent/80">Export PDF</button>
                   <button onClick={fetchData} className="px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90">Refresh Data</button>
                </div>
              </div>

              {/* KPIs */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {kpis ? (
                  <>
                    <KpiCard 
                      label="Total Revenue" 
                      value={`$${kpis.revenue.value.toLocaleString()}`} 
                      trend={kpis.revenue.trend} 
                      trendValue={kpis.revenue.change_pct} 
                      icon={TrendingUp}
                      color="bg-emerald-500"
                    />
                    <KpiCard 
                      label="Total Orders" 
                      value={kpis.orders.value.toLocaleString()} 
                      trend={kpis.orders.trend} 
                      trendValue={kpis.orders.change_pct} 
                      icon={Package}
                      color="bg-blue-500"
                    />
                    <KpiCard 
                      label="Active Customers" 
                      value={kpis.customers.value.toLocaleString()} 
                      trend={kpis.customers.trend} 
                      trendValue={kpis.customers.change_pct} 
                      icon={Users}
                      color="bg-purple-500"
                    />
                    <KpiCard 
                      label="Avg. Order Value" 
                      value={`$${kpis.avg_order_value.value.toLocaleString()}`} 
                      trend={kpis.avg_order_value.trend} 
                      trendValue={kpis.avg_order_value.change_pct} 
                      icon={Zap}
                      color="bg-amber-500"
                    />
                  </>
                ) : (
                  [...Array(4)].map((_, i) => <div key={i} className="h-32 bg-accent animate-pulse rounded-xl" />)
                )}
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Revenue Trend Chart */}
                <div className="lg:col-span-2 glass-card p-6 rounded-xl min-h-[400px] flex flex-col">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-bold">Revenue & Forecasting</h3>
                    <div className="flex items-center gap-4 text-xs font-medium">
                       <div className="flex items-center gap-1.5"><span className="w-3 h-3 bg-primary rounded-full"></span> Actual</div>
                       <div className="flex items-center gap-1.5"><span className="w-3 h-1 border-t-2 border-primary border-dashed"></span> Forecast</div>
                    </div>
                  </div>
                  <div className="flex-1">
                    <ResponsiveContainer width="100%" height={320}>
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--muted)/0.2)" />
                        <XAxis 
                          dataKey="date" 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                          minTickGap={30}
                        />
                        <YAxis 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fill: 'hsl(var(--muted-foreground))', fontSize: 12}}
                          tickFormatter={(v) => `$${v/1000}k`}
                        />
                        <Tooltip 
                          contentStyle={{backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: '8px'}}
                          itemStyle={{color: 'hsl(var(--foreground))'}}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="revenue" 
                          stroke="hsl(var(--primary))" 
                          strokeWidth={3}
                          fillOpacity={1} 
                          fill="url(#colorRevenue)" 
                          strokeDasharray={ (d) => d.type === 'forecast' ? '5 5' : '0' }
                          connectNulls
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* AI Insights Panel */}
                <div className="flex flex-col gap-6">
                   <div className="glass-card p-6 rounded-xl flex-1">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                          <BrainCircuit className="text-primary" size={20} />
                          AI Insights
                        </h3>
                        <button className="text-xs text-primary font-medium hover:underline">View All</button>
                      </div>
                      <div className="space-y-2">
                        {insights.length > 0 ? (
                          insights.map((insight, i) => <InsightCard key={i} insight={insight} />)
                        ) : (
                          <div className="text-center py-12 text-muted-foreground italic">
                             Generating insights...
                          </div>
                        )}
                      </div>
                   </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Segments */}
                <div className="glass-card p-6 rounded-xl">
                   <h3 className="text-lg font-bold mb-6">Customer Segments</h3>
                   <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                         <BarChart data={segments} layout="vertical">
                            <XAxis type="number" hide />
                            <YAxis dataKey="segment" type="category" axisLine={false} tickLine={false} tick={{fill: 'hsl(var(--foreground))', fontSize: 12}} width={120} />
                            <Tooltip 
                              cursor={{fill: 'transparent'}}
                              contentStyle={{backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: '8px'}}
                            />
                            <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
                               {segments.map((entry, index) => (
                                 <Cell key={`cell-${index}`} fill={`hsl(var(--primary) / ${1 - index*0.15})`} />
                               ))}
                            </Bar>
                         </BarChart>
                      </ResponsiveContainer>
                   </div>
                </div>

                {/* Top Products */}
                <div className="glass-card p-6 rounded-xl overflow-hidden">
                   <h3 className="text-lg font-bold mb-6">Top Performing Products</h3>
                   <div className="space-y-4">
                      {topProducts.map((product, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-accent/30 transition-colors group">
                           <div className="flex items-center gap-4">
                              <div className="w-10 h-10 rounded-lg bg-accent flex items-center justify-center text-sm font-bold">
                                {i + 1}
                              </div>
                              <div>
                                 <h4 className="font-medium text-sm">{product.name}</h4>
                                 <p className="text-xs text-muted-foreground">{product.category}</p>
                              </div>
                           </div>
                           <div className="text-right">
                              <p className="font-bold">${product.revenue.toLocaleString()}</p>
                              <p className="text-[10px] text-emerald-400 font-medium">+{product.quantity_sold} units</p>
                           </div>
                        </div>
                      ))}
                   </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto h-full flex flex-col animate-in">
               <div className="flex-1 space-y-6 mb-8 overflow-y-auto p-4 custom-scrollbar">
                  {!chatResponse && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                       <div className="bg-primary/20 p-6 rounded-full mb-4">
                          <BrainCircuit size={48} className="text-primary" />
                       </div>
                       <h2 className="text-3xl font-bold">Ask Your Data</h2>
                       <p className="text-muted-foreground max-w-md">
                         Query your business data using natural language. Try asking "Who are my top 5 customers?" or "Show me revenue trend for last week."
                       </p>
                    </div>
                  )}

                  {chatResponse && (
                    <div className="space-y-6">
                       <div className="flex justify-end">
                          <div className="bg-primary text-white p-4 rounded-2xl rounded-tr-none max-w-[80%] shadow-lg">
                             {chatQuery}
                          </div>
                       </div>
                       <div className="flex justify-start">
                          <div className="glass-card p-6 rounded-2xl rounded-tl-none max-w-[90%] border-l-4 border-l-primary">
                             <div className="flex items-center gap-2 mb-4 text-primary font-bold text-xs">
                                <BrainCircuit size={16} /> AI ANALYST
                             </div>
                             <div className="prose prose-invert prose-sm max-w-none mb-6">
                                {chatResponse.answer}
                             </div>
                             
                             {chatResponse.data && chatResponse.data.length > 0 && (
                               <div className="overflow-x-auto rounded-lg border border-border">
                                  <table className="w-full text-left text-xs">
                                     <thead className="bg-accent">
                                        <tr>
                                           {Object.keys(chatResponse.data[0]).map(key => (
                                             <th key={key} className="p-3 font-bold uppercase tracking-wider">{key}</th>
                                           ))}
                                        </tr>
                                     </thead>
                                     <tbody>
                                        {chatResponse.data.map((row, i) => (
                                          <tr key={i} className="border-t border-border hover:bg-accent/20">
                                             {Object.values(row).map((val, j) => (
                                               <td key={j} className="p-3">{String(val)}</td>
                                             ))}
                                          </tr>
                                        ))}
                                     </tbody>
                                  </table>
                               </div>
                             )}
                          </div>
                       </div>
                    </div>
                  )}
               </div>

               <form onSubmit={handleChat} className="flex gap-4 p-4 glass-card rounded-2xl mb-8 items-center border-t border-primary/20">
                  <input 
                    type="text" 
                    value={chatQuery}
                    onChange={(e) => setChatQuery(e.target.value)}
                    placeholder="Type your question here..." 
                    className="flex-1 bg-transparent border-none focus:outline-none text-lg px-2"
                  />
                  <button 
                    disabled={isChatLoading}
                    className="bg-primary text-white p-3 rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isChatLoading ? <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <ChevronRight size={24} />}
                  </button>
               </form>
            </div>
          )}

          {(activeTab === 'customers' || activeTab === 'products') && (
            <div className="h-full flex items-center justify-center text-center py-20 animate-in">
               <div className="space-y-4">
                  <div className="text-6xl mb-4">🚧</div>
                  <h2 className="text-2xl font-bold">Under Construction</h2>
                  <p className="text-muted-foreground">The {activeTab} management interface is currently being optimized for large scale datasets.</p>
                  <button onClick={() => setActiveTab('dashboard')} className="text-primary font-medium hover:underline">Return to Dashboard</button>
               </div>
            </div>
          )}
        </div>
      </main>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: hsl(var(--muted)/0.3);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: hsl(var(--muted)/0.5);
        }
      `}</style>
    </div>
  );
}
