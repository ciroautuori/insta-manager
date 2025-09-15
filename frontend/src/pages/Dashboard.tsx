import React from 'react'
import { useDashboard } from '@/contexts/DashboardContext'
import Header from '@/components/layout/Header'
import StatsCard from '@/components/dashboard/StatsCard'
import RecentActivity from '@/components/dashboard/RecentActivity'
import AccountOverview from '@/components/dashboard/AccountOverview'
import ScheduledPosts from '@/components/dashboard/ScheduledPosts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import { 
  Users, 
  FileText, 
  Calendar,
  Image,
  TrendingUp,
  Heart,
  Eye,
  Plus,
  RefreshCw
} from 'lucide-react'

const Dashboard: React.FC = () => {
  const { 
    stats, 
    accounts, 
    selectedAccount,
    loading, 
    error,
    refreshStats,
    refreshAccounts
  } = useDashboard()

  // Mock data per attività recenti e post programmati
  // In un'app reale, questi verrebbero dal backend
  const mockRecentActivity = [
    {
      id: '1',
      type: 'post_published' as const,
      title: 'Post pubblicato con successo',
      description: 'Il post "Nuova collezione primavera" è stato pubblicato',
      timestamp: new Date(Date.now() - 300000).toISOString(), // 5 min fa
      metadata: {
        account_username: accounts[0]?.username || 'account1',
        account_avatar: accounts[0]?.profile_picture_url
      }
    },
    {
      id: '2',
      type: 'media_uploaded' as const,
      title: 'Media caricato',
      description: '3 immagini caricate per il prossimo post',
      timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 min fa
      metadata: {
        media_count: 3
      }
    },
    {
      id: '3',
      type: 'analytics_synced' as const,
      title: 'Analytics sincronizzate',
      description: 'Dati analytics aggiornati per tutti gli account',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 ora fa
    }
  ]

  const mockScheduledPosts = [
    {
      id: '1',
      account_username: accounts[0]?.username || 'account1',
      account_avatar: accounts[0]?.profile_picture_url,
      post_type: 'feed' as const,
      content: 'Oggi condividiamo con voi la nostra nuova collezione! Cosa ne pensate? #fashion #newcollection',
      media_files: ['image1.jpg', 'image2.jpg'],
      scheduled_time: new Date(Date.now() + 3600000).toISOString(), // tra 1 ora
      status: 'pending' as const,
      retry_count: 0
    },
    {
      id: '2', 
      account_username: accounts[1]?.username || 'account2',
      account_avatar: accounts[1]?.profile_picture_url,
      post_type: 'story' as const,
      content: 'Behind the scenes del nostro shooting fotografico!',
      media_files: ['video1.mp4'],
      scheduled_time: new Date(Date.now() + 7200000).toISOString(), // tra 2 ore
      status: 'pending' as const,
      retry_count: 0
    }
  ]

  const handleRefresh = () => {
    refreshStats()
    refreshAccounts()
  }

  if (loading) return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="animate-pulse">
              <div className="h-4 bg-muted rounded w-1/2 mb-2"></div>
              <div className="h-6 bg-muted rounded w-1/3"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  )

  if (error) {
    return (
      <div className="flex-1 space-y-4 p-8 pt-6">
        <Header />
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-destructive mb-4">
              <TrendingUp className="h-12 w-12" />
            </div>
            <h3 className="text-lg font-medium mb-2">Errore nel caricamento dei dati</h3>
            <p className="text-muted-foreground mb-4 text-center">
              Si è verificato un errore durante il caricamento delle statistiche.
            </p>
            <Button onClick={handleRefresh}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Riprova
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Header />
      
      {/* Statistiche principali */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Account Connessi"
          value={stats?.total_accounts || accounts.length}
          description={selectedAccount ? `Account selezionato: @${selectedAccount.username}` : "Tutti gli account"}
          icon={Users}
          trend={{
            value: 5.2,
            label: "dal mese scorso",
            isPositive: true
          }}
        />
        
        <StatsCard
          title="Post Pubblicati"
          value={stats?.total_posts || 0}
          description="Post totali pubblicati"
          icon={FileText}
          trend={{
            value: 12.5,
            label: "questa settimana",
            isPositive: true
          }}
        />
        
        <StatsCard
          title="Post Programmati"
          value={stats?.scheduled_posts || mockScheduledPosts.length}
          description="Post in attesa di pubblicazione"
          icon={Calendar}
          trend={{
            value: 8.1,
            label: "vs settimana scorsa",
            isPositive: true
          }}
        />
        
        <StatsCard
          title="Media Caricati"
          value={stats?.total_media || 0}
          description="File multimediali totali"
          icon={Image}
          trend={{
            value: 3.2,
            label: "oggi",
            isPositive: true
          }}
        />
      </div>

      {/* Statistiche engagement se c'è un account selezionato */}
      {selectedAccount && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatsCard
            title="Follower"
            value={selectedAccount.followers_count}
            description={`@${selectedAccount.username}`}
            icon={Users}
            trend={{
              value: 2.4,
              label: "questa settimana",
              isPositive: true
            }}
          />
          
          <StatsCard
            title="Media Pubblicati"
            value={selectedAccount.media_count}
            description="Post totali sull'account"
            icon={Image}
          />
          
          <StatsCard
            title="Engagement Rate"
            value={`${(Math.random() * 5 + 2).toFixed(1)}%`}
            description="Media ultimi 10 post"
            icon={Heart}
            trend={{
              value: 1.2,
              label: "vs mese scorso",
              isPositive: true
            }}
          />
          
          <StatsCard
            title="Reach Medio"
            value={Math.floor(selectedAccount.followers_count * (0.15 + Math.random() * 0.1))}
            description="Per post negli ultimi 7 giorni"
            icon={Eye}
            trend={{
              value: -2.1,
              label: "vs settimana scorsa",
              isPositive: false
            }}
          />
        </div>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Azioni Rapide</CardTitle>
          <CardDescription>
            Accesso rapido alle funzionalità più utilizzate
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button asChild>
              <Link to="/posts/new">
                <Plus className="mr-2 h-4 w-4" />
                Nuovo Post
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/scheduled">
                <Calendar className="mr-2 h-4 w-4" />
                Programma Post
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/media">
                <Image className="mr-2 h-4 w-4" />
                Carica Media
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/analytics">
                <TrendingUp className="mr-2 h-4 w-4" />
                Visualizza Analytics
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Dashboard content */}
      <div className="grid gap-4 lg:grid-cols-7">
        {/* Account Overview */}
        <div className="lg:col-span-4">
          <AccountOverview accounts={accounts} />
        </div>
        
        {/* Recent Activity */}
        <div className="lg:col-span-3">
          <RecentActivity activities={mockRecentActivity} />
        </div>
      </div>

      {/* Scheduled Posts */}
      <ScheduledPosts posts={mockScheduledPosts} />
    </div>
  )
}

export default Dashboard
