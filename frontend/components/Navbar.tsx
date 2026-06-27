import { Zap, LayoutDashboard, Settings, Menu, Folder, Bell, User } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavbarProps {
  onLogoClick?: () => void;
}

export default function Navbar({ onLogoClick }: NavbarProps) {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path 
      ? 'bg-white text-slate-900 shadow-sm ring-1 ring-slate-200' 
      : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100';
  };

  return (
    <>
      <nav className="sticky top-0 z-40 w-full backdrop-blur-xl bg-white/80 border-b border-slate-200/60 supports-[backdrop-filter]:bg-white/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo Section */}
            <div 
              onClick={onLogoClick}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-blue-600 blur-lg opacity-20 group-hover:opacity-40 transition-opacity rounded-full"></div>
                <div className="relative bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
                  <Zap size={20} fill="currentColor" className="text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 tracking-tight">
                  LeadGen
                </h1>
                <p className="text-[10px] uppercase tracking-widest font-bold text-blue-600/80">Intelligence</p>
              </div>
            </div>

            {/* Pill Navigation (Center) */}
            <div className="hidden md:flex items-center bg-slate-100/50 p-1 rounded-full border border-slate-200/60 backdrop-blur-sm">
              <Link href="/" className={`flex items-center gap-2 px-5 py-2 rounded-full font-medium text-sm transition-all duration-200 ${isActive('/')}`}>
                <LayoutDashboard size={16} /> <span className="hidden lg:inline">Dashboard</span>
              </Link>
              <Link 
                href="/projects"
                className={`flex items-center gap-2 px-5 py-2 rounded-full font-medium text-sm transition-all duration-200 ${isActive('/projects')}`}
              >
                <Folder size={16} /> <span className="hidden lg:inline">Projects</span>
              </Link>
              <Link 
                href="/settings"
                className={`flex items-center gap-2 px-5 py-2 rounded-full font-medium text-sm transition-all duration-200 ${isActive('/settings')}`}
              >
                <Settings size={16} /> <span className="hidden lg:inline">Settings</span>
              </Link>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-3">
              <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors relative">
                <Bell size={20} />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
              </button>
              
              <div className="h-6 w-px bg-slate-200 mx-1"></div>
              
              <button className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-full hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-200">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-100 to-blue-100 border border-indigo-200 flex items-center justify-center text-indigo-600 shadow-sm">
                   <User size={16} />
                </div>
                <div className="hidden sm:block text-left">
                    <p className="text-xs font-bold text-slate-700">Admin</p>
                    <p className="text-[10px] text-slate-400">Pro Plan</p>
                </div>
              </button>
              
              <button className="md:hidden text-slate-500 p-2">
                <Menu size={24} />
              </button>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}
