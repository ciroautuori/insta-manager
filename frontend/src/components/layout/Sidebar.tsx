import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { 
  Home, 
 
  FileText, 
  Calendar, 
  Image, 
  BarChart3, 
  Instagram,
  Clock
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Account Instagram', href: '/accounts', icon: Instagram },
  { name: 'Post', href: '/posts', icon: FileText },
  { name: 'Programmati', href: '/scheduled', icon: Clock },
  { name: 'Media', href: '/media', icon: Image },
  { name: 'Calendario', href: '/calendar', icon: Calendar },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
]

interface SidebarProps {
  className?: string
}

const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const location = useLocation()

  return (
    <div className={cn("pb-12 min-h-screen bg-card border-r", className)}>
      <div className="space-y-4 py-4">
        <div className="px-3 py-2">
          <div className="flex items-center pl-3 mb-14">
            <Instagram className="h-8 w-8 text-primary mr-3" />
            <h1 className="text-xl font-bold">Instagram Manager</h1>
          </div>
          <div className="space-y-1">
            <nav className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    )}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
