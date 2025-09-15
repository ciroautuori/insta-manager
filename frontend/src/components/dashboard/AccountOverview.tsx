import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Link } from 'react-router-dom'
import { 
  Users, 
  MessageCircle, 
  Heart, 
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react'
import { formatNumber } from '@/lib/utils'

import { InstagramAccount } from '@/contexts/DashboardContext'

interface AccountOverviewProps {
  accounts: InstagramAccount[]
  className?: string
}

const AccountOverview: React.FC<AccountOverviewProps> = ({ accounts, className }) => {
  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return <Minus className="h-4 w-4 text-gray-600" />
    }
  }

  if (!accounts.length) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Account Instagram</CardTitle>
          <CardDescription>Nessun account connesso</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <div className="mx-auto h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">Nessun Account Connesso</h3>
            <p className="text-muted-foreground mb-4">
              Connetti il tuo primo account Instagram per iniziare
            </p>
            <Button asChild>
              <Link to="/accounts">Connetti Account</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Account Instagram</CardTitle>
          <CardDescription>
            {accounts.length} account{accounts.length > 1 ? 's' : ''} connesso{accounts.length > 1 ? 's' : ''}
          </CardDescription>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link to="/accounts">
            Gestisci
            <ExternalLink className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {accounts.slice(0, 4).map((account) => (
            <div key={account.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={account.profile_picture_url} />
                  <AvatarFallback>{account.username.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium">@{account.username}</h4>
                    {account.is_business && (
                      <Badge variant="secondary" className="text-xs">Business</Badge>
                    )}
                    {!account.is_connected && (
                      <Badge variant="destructive" className="text-xs">Disconnesso</Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">{account.full_name}</p>
                  
                  <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>{formatNumber(account.followers_count)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MessageCircle className="h-4 w-4" />
                      <span>{formatNumber(account.media_count)}</span>
                    </div>
                    {account.engagement_rate && (
                      <div className="flex items-center space-x-1">
                        <Heart className="h-4 w-4" />
                        <span>{account.engagement_rate.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                {account.recent_posts_performance && (
                  <div className="flex items-center space-x-2 mb-2">
                    {getTrendIcon(account.recent_posts_performance.trend)}
                    <div className="text-sm">
                      <div className="font-medium">
                        {formatNumber(account.recent_posts_performance.avg_likes)} like
                      </div>
                      <div className="text-muted-foreground">
                        {formatNumber(account.recent_posts_performance.avg_comments)} commenti
                      </div>
                    </div>
                  </div>
                )}
                
                <p className="text-xs text-muted-foreground">Ultimo sync: {account.last_sync ? new Date(account.last_sync).toLocaleDateString('it-IT') : 'Mai'}</p>
              </div>
            </div>
          ))}
          
          {accounts.length > 4 && (
            <div className="text-center pt-4 border-t">
              <Button variant="ghost" asChild>
                <Link to="/accounts">
                  Visualizza tutti i {accounts.length} account
                </Link>
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default AccountOverview
