import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useDashboard } from '@/contexts/DashboardContext'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Bell, 
  RefreshCw, 
  User, 
  LogOut,
  ChevronDown
} from 'lucide-react'

const Header: React.FC = () => {
  const { admin, logout } = useAuth()
  const { selectedAccount, accounts, selectAccount, refreshStats, refreshAccounts } = useDashboard()

  const handleRefresh = () => {
    refreshStats()
    refreshAccounts()
  }

  const getInitials = (name?: string) => {
    if (!name) return 'AD'
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-foreground">
            {selectedAccount ? `Account: ${selectedAccount.username}` : 'Dashboard'}
          </h2>
          
          {accounts.length > 1 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="ml-2">
                  {selectedAccount?.username || 'Seleziona Account'}
                  <ChevronDown className="ml-2 h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56">
                <DropdownMenuLabel>Account Instagram</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => selectAccount(null)}
                  className={!selectedAccount ? 'bg-accent' : ''}
                >
                  Tutti gli account
                </DropdownMenuItem>
                {accounts.map((account) => (
                  <DropdownMenuItem
                    key={account.id}
                    onClick={() => selectAccount(account)}
                    className={selectedAccount?.id === account.id ? 'bg-accent' : ''}
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">@{account.username}</span>
                      <span className="text-xs text-muted-foreground">
                        {account.followers_count.toLocaleString()} follower
                      </span>
                    </div>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            className="h-9 w-9"
            title="Aggiorna dati"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9"
            title="Notifiche"
          >
            <Bell className="h-4 w-4" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                <Avatar className="h-9 w-9">
                  <AvatarFallback>
                    {getInitials(admin?.full_name || admin?.email)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {admin?.full_name || 'Admin'}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {admin?.email}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profilo</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

export default Header
