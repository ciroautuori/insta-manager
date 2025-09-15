import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import { cn } from '@/lib/utils'

interface LayoutProps {
  className?: string
}

const Layout: React.FC<LayoutProps> = ({ className }) => {
  return (
    <div className={cn("min-h-screen bg-background", className)}>
      <div className="flex">
        <Sidebar className="w-64 fixed top-0 left-0 z-40" />
        <main className="flex-1 ml-64">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
