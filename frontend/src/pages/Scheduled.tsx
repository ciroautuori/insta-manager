import React, { useState } from 'react'
import { useDashboard } from '@/contexts/DashboardContext'
import Header from '@/components/layout/Header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Calendar } from '@/components/ui/calendar'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { Link } from 'react-router-dom'
import { 
  Calendar as CalendarIcon,
  Clock,
  Plus,
  Play,
  Pause,
  Trash2,
  Edit,
  Image,
  Video,
  FileText,
  PlayCircle,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { format, isSameDay } from 'date-fns'
import { it } from 'date-fns/locale'
import { cn } from '@/lib/utils'

interface ScheduledPost {
  id: string
  account_username: string
  account_avatar?: string
  post_type: 'feed' | 'story' | 'reel'
  content: string
  media_files: string[]
  scheduled_time: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  retry_count: number
  max_retries: number
  error_message?: string
  celery_task_id?: string
}

const Scheduled: React.FC = () => {
  const { accounts } = useDashboard()
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [accountFilter, setAccountFilter] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar')

  // Mock data - in produzione verrebbe dall'API
  const mockScheduledPosts: ScheduledPost[] = [
    {
      id: '1',
      account_username: accounts[0]?.username || 'account1',
      account_avatar: accounts[0]?.profile_picture_url,
      post_type: 'feed',
      content: 'Nuovo prodotto in arrivo! Non perdere il lancio di domani alle 15:00 🚀 #newproduct #launch',
      media_files: ['product1.jpg', 'product2.jpg'],
      scheduled_time: new Date(Date.now() + 3600000).toISOString(), // tra 1 ora
      status: 'pending',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: '2',
      account_username: accounts[0]?.username || 'account1',
      account_avatar: accounts[0]?.profile_picture_url,
      post_type: 'story',
      content: 'Behind the scenes della sessione fotografica! 📸',
      media_files: ['bts1.mp4'],
      scheduled_time: new Date(Date.now() + 7200000).toISOString(), // tra 2 ore
      status: 'pending',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: '3',
      account_username: accounts[1]?.username || 'account2',
      account_avatar: accounts[1]?.profile_picture_url,
      post_type: 'reel',
      content: 'Tutorial makeup veloce per la sera! ✨ #makeup #tutorial #evening',
      media_files: ['tutorial.mp4'],
      scheduled_time: new Date(Date.now() + 86400000).toISOString(), // domani
      status: 'pending',
      retry_count: 0,
      max_retries: 3
    },
    {
      id: '4',
      account_username: accounts[0]?.username || 'account1',
      post_type: 'feed',
      content: 'Post fallito durante la pubblicazione',
      media_files: ['error.jpg'],
      scheduled_time: new Date(Date.now() - 3600000).toISOString(), // 1 ora fa
      status: 'failed',
      retry_count: 2,
      max_retries: 3,
      error_message: 'Token Instagram scaduto'
    },
    {
      id: '5',
      account_username: accounts[1]?.username || 'account2',
      post_type: 'feed',
      content: 'Post pubblicato con successo!',
      media_files: ['success.jpg'],
      scheduled_time: new Date(Date.now() - 86400000).toISOString(), // ieri
      status: 'completed',
      retry_count: 0,
      max_retries: 3
    }
  ]


  const filteredPosts = mockScheduledPosts.filter(post => {
    const matchesStatus = statusFilter === 'all' || post.status === statusFilter
    const matchesAccount = accountFilter === 'all' || post.account_username === accountFilter
    const matchesDate = viewMode === 'list' || isSameDay(new Date(post.scheduled_time), selectedDate)
    
    return matchesStatus && matchesAccount && matchesDate
  })

  const getPostsForDate = (date: Date) => {
    return mockScheduledPosts.filter(post => 
      isSameDay(new Date(post.scheduled_time), date)
    )
  }

  const handleExecuteNow = async (postId: string) => {
    console.log('Esecuzione immediata post:', postId)
    // Implementazione API call
  }

  const handleCancelPost = async (postId: string) => {
    console.log('Annullamento post:', postId)
    // Implementazione API call
  }

  const handleDeletePost = async (postId: string) => {
    console.log('Eliminazione post:', postId)
    // Implementazione API call
  }

  const hasPostsOnDate = (date: Date) => {
    return getPostsForDate(date).length > 0
  }

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <Header />
      
      {/* Header sezione */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Post Programmati</h1>
          <p className="text-muted-foreground">
            Gestisci i tuoi contenuti programmati
          </p>
        </div>
        <div className="flex space-x-2">
          <div className="flex bg-muted rounded-lg p-1">
            <Button
              variant={viewMode === 'calendar' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('calendar')}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              Calendario
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <Clock className="mr-2 h-4 w-4" />
              Lista
            </Button>
          </div>
          <Button asChild>
            <Link to="/posts/schedule">
              <Plus className="mr-2 h-4 w-4" />
              Programma Post
            </Link>
          </Button>
        </div>
      </div>

      {/* Statistiche */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Attesa</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockScheduledPosts.filter(p => p.status === 'pending').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completati</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockScheduledPosts.filter(p => p.status === 'completed').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Falliti</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockScheduledPosts.filter(p => p.status === 'failed').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Oggi</CardTitle>
            <CalendarIcon className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {getPostsForDate(new Date()).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtri */}
      <Card>
        <CardHeader>
          <CardTitle>Filtri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtra per stato" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutti gli stati</SelectItem>
                <SelectItem value="pending">In attesa</SelectItem>
                <SelectItem value="processing">In corso</SelectItem>
                <SelectItem value="completed">Completati</SelectItem>
                <SelectItem value="failed">Falliti</SelectItem>
                <SelectItem value="cancelled">Annullati</SelectItem>
              </SelectContent>
            </Select>

            {accounts.length > 1 && (
              <Select value={accountFilter} onValueChange={setAccountFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filtra per account" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tutti gli account</SelectItem>
                  {accounts.map(account => (
                    <SelectItem key={account.id} value={account.username}>
                      @{account.username}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardContent>
      </Card>

      {viewMode === 'calendar' ? (
        /* Vista Calendario */
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Calendario</CardTitle>
              <CardDescription>
                Seleziona una data per visualizzare i post programmati
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={(date) => date && setSelectedDate(date)}
                modifiers={{
                  hasEvents: (date) => hasPostsOnDate(date)
                }}
                modifiersStyles={{
                  hasEvents: {
                    backgroundColor: 'hsl(var(--primary))',
                    color: 'hsl(var(--primary-foreground))',
                    fontWeight: 'bold'
                  }
                }}
                className="rounded-md border"
              />
              <div className="mt-4 text-sm text-muted-foreground">
                <p>Le date evidenziate hanno post programmati</p>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>
                Post per {format(selectedDate, 'dd MMMM yyyy', { locale: it })}
              </CardTitle>
              <CardDescription>
                {filteredPosts.length} post programmati per questa data
              </CardDescription>
            </CardHeader>
            <CardContent>
              {filteredPosts.length === 0 ? (
                <div className="text-center py-8">
                  <CalendarIcon className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    Nessun post programmato per questa data
                  </p>
                  <Button variant="outline" className="mt-4" asChild>
                    <Link to="/posts/schedule">
                      <Plus className="mr-2 h-4 w-4" />
                      Programma Post
                    </Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredPosts
                    .sort((a, b) => new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime())
                    .map((post) => (
                      <ScheduledPostCard 
                        key={post.id} 
                        post={post}
                        onExecute={() => handleExecuteNow(post.id)}
                        onCancel={() => handleCancelPost(post.id)}
                        onDelete={() => handleDeletePost(post.id)}
                      />
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        /* Vista Lista */
        <Card>
          <CardHeader>
            <CardTitle>Tutti i Post Programmati</CardTitle>
            <CardDescription>
              {filteredPosts.length} post corrispondono ai filtri selezionati
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredPosts.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  Nessun post programmato corrisponde ai filtri
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredPosts
                  .sort((a, b) => new Date(a.scheduled_time).getTime() - new Date(b.scheduled_time).getTime())
                  .map((post) => (
                    <ScheduledPostCard 
                      key={post.id} 
                      post={post}
                      onExecute={() => handleExecuteNow(post.id)}
                      onCancel={() => handleCancelPost(post.id)}
                      onDelete={() => handleDeletePost(post.id)}
                      showDate={true}
                    />
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

interface ScheduledPostCardProps {
  post: ScheduledPost
  onExecute: () => void
  onCancel: () => void
  onDelete: () => void
  showDate?: boolean
}

const ScheduledPostCard: React.FC<ScheduledPostCardProps> = ({ 
  post, 
  onExecute, 
  onCancel, 
  onDelete, 
  showDate = false 
}) => {
  const PostIcon = getPostTypeIcon(post.post_type)
  const StatusIcon = getStatusIcon(post.status)
  const scheduledTime = new Date(post.scheduled_time)
  const isOverdue = post.status === 'pending' && scheduledTime < new Date()

  return (
    <div className={cn(
      "flex items-start space-x-4 p-4 border rounded-lg",
      isOverdue && "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950"
    )}>
      <div className="flex-shrink-0">
        <div className="relative">
          <Avatar className="h-10 w-10">
            <AvatarImage src={post.account_avatar} />
            <AvatarFallback>
              {post.account_username.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-background border-2 border-background rounded-full flex items-center justify-center">
            {PostIcon}
          </div>
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between mb-2">
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-medium text-sm">@{post.account_username}</span>
              <Badge variant="secondary" className="text-xs capitalize">
                {post.post_type}
              </Badge>
              {getStatusBadge(post.status)}
              {isOverdue && (
                <Badge variant="destructive" className="text-xs">
                  In ritardo
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
              <div className="flex items-center space-x-1">
                {StatusIcon}
                <span>
                  {format(scheduledTime, 
                    showDate ? 'dd MMM yyyy, HH:mm' : 'HH:mm', 
                    { locale: it }
                  )}
                </span>
              </div>
              {post.media_files.length > 0 && (
                <div className="flex items-center space-x-1">
                  <Image className="h-3 w-3" />
                  <span>{post.media_files.length}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex space-x-1">
            {post.status === 'pending' && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onExecute}
                className="h-8 w-8 p-0"
                title="Esegui ora"
              >
                <Play className="h-3 w-3" />
              </Button>
            )}
            
            {post.status === 'pending' && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm"
                    className="h-8 w-8 p-0"
                    title="Annulla"
                  >
                    <Pause className="h-3 w-3" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Annulla Post Programmato</AlertDialogTitle>
                    <AlertDialogDescription>
                      Sei sicuro di voler annullare questo post programmato?
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Mantieni</AlertDialogCancel>
                    <AlertDialogAction onClick={onCancel}>
                      Annulla Post
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}

            <Button variant="outline" size="sm" className="h-8 w-8 p-0" asChild>
              <Link to={`/posts/scheduled/${post.id}/edit`}>
                <Edit className="h-3 w-3" />
              </Link>
            </Button>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm"
                  className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Elimina Post Programmato</AlertDialogTitle>
                  <AlertDialogDescription>
                    Sei sicuro di voler eliminare definitivamente questo post programmato?
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Annulla</AlertDialogCancel>
                  <AlertDialogAction
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    onClick={onDelete}
                  >
                    Elimina
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
          {post.content}
        </p>

        {post.status === 'failed' && post.error_message && (
          <div className="flex items-center space-x-2 text-xs text-red-600 bg-red-50 dark:bg-red-950 p-2 rounded">
            <AlertCircle className="h-3 w-3" />
            <span>{post.error_message}</span>
            <span className="ml-auto">Tentativo {post.retry_count}/{post.max_retries}</span>
          </div>
        )}

        {post.retry_count > 0 && post.status !== 'failed' && (
          <div className="text-xs text-muted-foreground">
            Tentativi: {post.retry_count}/{post.max_retries}
          </div>
        )}
      </div>
    </div>
  )
}

function getPostTypeIcon(type: string) {
  switch (type) {
    case 'story':
      return <Image className="h-3 w-3 text-muted-foreground" />
    case 'reel':
      return <Video className="h-3 w-3 text-muted-foreground" />
    default:
      return <FileText className="h-3 w-3 text-muted-foreground" />
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-3 w-3 text-green-600" />
    case 'processing':
      return <PlayCircle className="h-3 w-3 text-blue-600 animate-pulse" />
    case 'failed':
      return <XCircle className="h-3 w-3 text-red-600" />
    case 'cancelled':
      return <XCircle className="h-3 w-3 text-gray-600" />
    default:
      return <Clock className="h-3 w-3 text-yellow-600" />
  }
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'completed':
      return <Badge className="bg-green-100 text-green-800 text-xs">Pubblicato</Badge>
    case 'processing':
      return <Badge className="bg-blue-100 text-blue-800 text-xs">In corso</Badge>
    case 'failed':
      return <Badge variant="destructive" className="text-xs">Fallito</Badge>
    case 'cancelled':
      return <Badge variant="secondary" className="text-xs">Annullato</Badge>
    default:
      return <Badge className="bg-yellow-100 text-yellow-800 text-xs">In attesa</Badge>
  }
}

export default Scheduled
