import React, { useState } from 'react'
import { useDashboard } from '@/contexts/DashboardContext'
import Header from '@/components/layout/Header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { 
  Users, 
  Plus, 
  Settings,
  Trash2,
  RefreshCw,
  ExternalLink,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Heart,
  MessageCircle,
  Calendar
} from 'lucide-react'
import { formatNumber, formatDate } from '@/lib/utils'
import { instagramApi } from '@/lib/api'
import { InstagramAccount } from '@/contexts/DashboardContext'

const Accounts: React.FC = () => {
  const { accounts, refreshAccounts, selectAccount, selectedAccount } = useDashboard()
  const [isLoading, setIsLoading] = useState(false)

  const handleConnectAccount = async () => {
    try {
      setIsLoading(true)
      const response = await instagramApi.getAuthUrl()
      // Apri in una nuova finestra
      window.open(response.auth_url, '_blank', 'width=500,height=600')
    } catch (error) {
      console.error('Errore nella connessione:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSyncAccount = async (accountId: number) => {
    try {
      setIsLoading(true)
      await instagramApi.syncAccount(accountId)
      await refreshAccounts()
    } catch (error) {
      console.error('Errore nel sync:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteAccount = async (accountId: number) => {
    try {
      await instagramApi.deleteAccount(accountId)
      await refreshAccounts()
      // Se l'account cancellato era selezionato, deselezionalo
      if (selectedAccount?.id === accountId) {
        selectAccount(null)
      }
    } catch (error) {
      console.error('Errore nella rimozione:', error)
    }
  }

  const getConnectionStatus = (account: InstagramAccount) => {
    if (!account.is_connected) {
      return {
        icon: XCircle,
        label: 'Disconnesso',
        color: 'text-destructive',
        bgColor: 'bg-destructive/10'
      }
    }

    // Verifica se la sincronizzazione è recente (meno di 24 ore)
    const lastSyncTime = account.last_sync ? new Date(account.last_sync).getTime() : 0
    const now = new Date().getTime()
    const hoursDiff = (now - lastSyncTime) / (1000 * 60 * 60)

    if (hoursDiff > 24) {
      return {
        icon: AlertCircle,
        label: 'Sincronizzazione necessaria',
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50'
      }
    }

    return {
      icon: CheckCircle,
      label: 'Connesso',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  }

  const getPermissionsBadge = (permissions: string[]) => {
    const hasFullAccess = permissions.includes('instagram_basic') && 
                         permissions.includes('instagram_content_publish') && 
                         permissions.includes('pages_show_list')

    if (hasFullAccess) {
      return <Badge variant="secondary" className="bg-green-100 text-green-800">Accesso Completo</Badge>
    }

    if (permissions.includes('instagram_basic')) {
      return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Accesso Base</Badge>
    }

    return <Badge variant="destructive">Permessi Limitati</Badge>
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Header />
      
      {/* Header sezione */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Account Instagram</h1>
          <p className="text-muted-foreground">
            Gestisci i tuoi account Instagram connessi
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={refreshAccounts}
            disabled={isLoading}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Aggiorna
          </Button>
          <Button onClick={handleConnectAccount} disabled={isLoading}>
            <Plus className="mr-2 h-4 w-4" />
            Connetti Account
          </Button>
        </div>
      </div>

      {/* Statistiche generali */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Account Totali</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{accounts.length}</div>
            <p className="text-xs text-muted-foreground">
              {accounts.filter(a => a.is_connected).length} connessi
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Follower Totali</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(accounts.reduce((sum, acc) => sum + acc.followers_count, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              Tutti gli account
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Post Totali</CardTitle>
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(accounts.reduce((sum, acc) => sum + acc.media_count, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              Media pubblicati
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Engagement Medio</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {accounts.length > 0 
                ? (accounts.reduce((sum, acc) => sum + (acc.engagement_rate || 0), 0) / accounts.length).toFixed(1)
                : '0.0'
              }%
            </div>
            <p className="text-xs text-muted-foreground">
              Media tutti gli account
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Lista account */}
      {accounts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="mx-auto h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">Nessun Account Connesso</h3>
            <p className="text-muted-foreground mb-4 text-center">
              Connetti il tuo primo account Instagram per iniziare a gestire i contenuti
            </p>
            <Button onClick={handleConnectAccount} disabled={isLoading}>
              <Plus className="mr-2 h-4 w-4" />
              Connetti Primo Account
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          {accounts.map((account) => {
            const status = getConnectionStatus(account)
            const StatusIcon = status.icon

            return (
              <Card key={account.id} className={selectedAccount?.id === account.id ? 'ring-2 ring-primary' : ''}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4">
                      <Avatar className="h-16 w-16">
                        <AvatarImage src={account.profile_picture_url} />
                        <AvatarFallback className="text-lg">
                          {account.username.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <CardTitle className="text-xl">@{account.username}</CardTitle>
                          {account.is_business && (
                            <Badge variant="secondary">Business</Badge>
                          )}
                          {getPermissionsBadge(account.permissions)}
                          {selectedAccount?.id === account.id && (
                            <Badge className="bg-primary">Selezionato</Badge>
                          )}
                        </div>
                        <CardDescription className="text-base">
                          {account.full_name}
                        </CardDescription>
                        
                        <div className={`flex items-center space-x-2 mt-2 px-2 py-1 rounded-md ${status.bgColor}`}>
                          <StatusIcon className={`h-4 w-4 ${status.color}`} />
                          <span className={`text-sm font-medium ${status.color}`}>
                            {status.label}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => selectAccount(account)}
                        disabled={selectedAccount?.id === account.id}
                      >
                        {selectedAccount?.id === account.id ? 'Selezionato' : 'Seleziona'}
                      </Button>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSyncAccount(account.id)}
                        disabled={isLoading || !account.is_connected}
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Rimuovi Account</AlertDialogTitle>
                            <AlertDialogDescription>
                              Sei sicuro di voler rimuovere l'account @{account.username}? 
                              Questa azione non può essere annullata e dovrai riconnetterlo manualmente.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Annulla</AlertDialogCancel>
                            <AlertDialogAction
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                              onClick={() => handleDeleteAccount(account.id)}
                            >
                              Rimuovi
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  {/* Statistiche account */}
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {formatNumber(account.followers_count)}
                      </div>
                      <div className="text-sm text-muted-foreground">Follower</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {formatNumber(account.following_count)}
                      </div>
                      <div className="text-sm text-muted-foreground">Following</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {formatNumber(account.media_count)}
                      </div>
                      <div className="text-sm text-muted-foreground">Post</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">
                        {account.engagement_rate ? `${account.engagement_rate.toFixed(1)}%` : 'N/A'}
                      </div>
                      <div className="text-sm text-muted-foreground">Engagement</div>
                    </div>
                  </div>

                  {/* Info aggiuntive */}
                  <div className="flex items-center justify-between text-sm text-muted-foreground border-t pt-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <Calendar className="h-4 w-4" />
                        <span>Ultimo sync: {account.last_sync ? formatDate(account.last_sync) : 'Mai'}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Settings className="h-4 w-4" />
                        <span>Tipo: {account.account_type}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span>Permessi: {account.permissions.length}</span>
                      <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default Accounts
